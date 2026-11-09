from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import httpx

from backend.schemas import ProblemRequest, ClarificationRequest, TriageResponse
from backend.triage_engine import triage_initial_problem, triage_clarification
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage engine error: {str(e)}")

@app.post("/api/triage/answer", response_model=TriageResponse, tags=["Triage"])
def answer_clarification(request: ClarificationRequest):
    """Provide the follow-up answer. Returns final resolved checklist with matched services."""
    try:
        result = triage_clarification(request)
        log_session(result.session_id, result.domain, result.urgency, result.status, result.specific_issue)
        return result
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
    """Check if a local Ollama instance is running on port 11434."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return {"available": r.status_code == 200}
    except Exception:
        return {"available": False}
