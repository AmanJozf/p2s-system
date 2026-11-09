from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import httpx

from backend.schemas import ProblemRequest, ClarificationRequest, TriageResponse
from backend.triage_engine import triage_initial_problem, triage_clarification
from backend.llm_providers import LLMError, OllamaProvider, get_provider, get_active_name, set_active
from backend.knowledge_base import SERVICES_DATABASE
from backend.database import init_db, log_session, get_stats, clear_sessions, add_service_db

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()

app = FastAPI(
    title="P2S — Problem to Service API",
    description="AI-powered triage engine that routes everyday problems to verified support services.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# ── Frontend page routes ──────────────────────────────────────────────────────
PAGES = {
    "/":          "frontend/index.html",
    "/triage":    "frontend/triage.html",
    "/services":  "frontend/services.html",
    "/dashboard": "frontend/dashboard.html",
    "/history":   "frontend/history.html",
    "/about":     "frontend/about.html",
    "/admin":     "frontend/admin.html",
}

for route, filepath in PAGES.items():
    def make_handler(fp):
        def handler():
            return FileResponse(fp)
        return handler
    app.get(route, include_in_schema=False)(make_handler(filepath))

# ── Triage Endpoints ──────────────────────────────────────────────────────────
@app.post("/api/triage/start", response_model=TriageResponse, tags=["Triage"])
def start_triage(request: ProblemRequest):
    """Submit a plain-language problem. Returns follow-up question or resolved checklist."""
    try:
        result = triage_initial_problem(request.problem_description)
        log_session(result.session_id, result.domain, result.urgency, result.status, result.specific_issue)
        return result
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage engine error: {str(e)}")

@app.post("/api/triage/answer", response_model=TriageResponse, tags=["Triage"])
def answer_clarification(request: ClarificationRequest):
    """Provide the follow-up answer. Returns final resolved checklist with matched services."""
    try:
        result = triage_clarification(request)
        log_session(result.session_id, result.domain, result.urgency, result.status, result.specific_issue)
        return result
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage engine error: {str(e)}")

# ── Services Endpoint ─────────────────────────────────────────────────────────
@app.get("/api/services", tags=["Services"])
def get_all_services():
    """Returns the full curated knowledge base of verified support services."""
    return {"services": SERVICES_DATABASE}

# ── Stats / Dashboard ─────────────────────────────────────────────────────────
@app.get("/api/stats/summary", tags=["Analytics"])
def get_stats_summary():
    """Returns aggregated analytics data for the dashboard."""
    return get_stats()

# ── Admin Endpoints ───────────────────────────────────────────────────────────
class ServicePayload(BaseModel):
    name: str
    domain: str
    role: str
    official_link: str
    is_free: bool = True

@app.post("/api/admin/services", tags=["Admin"])
def admin_add_service(payload: ServicePayload):
    """Add a new service to the knowledge base."""
    try:
        add_service_db(payload.name, payload.domain, payload.role, payload.official_link, payload.is_free)
        # Also add to in-memory SERVICES_DATABASE for current session
        if payload.domain not in SERVICES_DATABASE:
            SERVICES_DATABASE[payload.domain] = []
        SERVICES_DATABASE[payload.domain].append({
            "name": payload.name,
            "role": payload.role,
            "official_link": payload.official_link,
            "is_free": payload.is_free
        })
        return {"status": "added", "service": payload.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/sessions", tags=["Admin"])
def admin_clear_sessions():
    """Clear all session records from the database."""
    clear_sessions()
    return {"status": "cleared"}

@app.get("/api/admin/ollama-status", tags=["Admin"])
async def check_ollama():
    """Report whether a local Ollama server is running and which models are installed."""
    ollama = get_provider("ollama")
    models = ollama.installed_models()
    return {"available": ollama.is_available(), "models": models, "selected_model": ollama.model}


class ProviderPayload(BaseModel):
    provider: str
    model: str | None = None


@app.get("/api/admin/provider", tags=["Admin"])
def get_provider_config():
    """Currently active LLM provider (gemini = cloud, ollama = local/offline)."""
    active = get_provider()
    return {"active": get_active_name(), "label": active.label,
            "gemini_model": get_provider("gemini").model, "ollama_model": get_provider("ollama").model}


@app.post("/api/admin/provider", tags=["Admin"])
def set_provider_config(payload: ProviderPayload):
    """Switch the active LLM provider at runtime, optionally changing its model."""
    name = payload.provider.lower()
    if name not in ("gemini", "ollama"):
        raise HTTPException(status_code=400, detail="provider must be 'gemini' or 'ollama'")
    if payload.model:
        get_provider(name).model = payload.model
    if name == "ollama":
        ollama = get_provider("ollama")
        if not ollama.is_available():
            raise HTTPException(status_code=503, detail="Ollama is not running on localhost:11434.")
        if ollama.model not in ollama.installed_models():
            raise HTTPException(status_code=409, detail=f"Model '{ollama.model}' is not installed. Run: ollama pull {ollama.model}")
    set_active(name)
    return {"active": name, "label": get_provider().label}
