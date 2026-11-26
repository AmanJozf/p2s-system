"""
Vector Semantic Search Engine for P2S (Problem-to-Service).
Computes semantic embeddings of all 24 verified Berlin services.
Performs cosine-similarity ranking to match citizen queries to the exact verified services.
"""
import os
import json
import math
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

CACHE_FILE = Path(__file__).parent / "service_embeddings.json"


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def _get_gemini_client():
    from google import genai
    from google.genai import types
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=4000),
    )


def build_service_catalog() -> list[dict]:
    from backend.knowledge_base import SERVICES_DATABASE
    catalog = []
    for domain, services in SERVICES_DATABASE.items():
        for s in services:
            # Combine domain, name, role and region into rich semantic representation
            text = f"Domain: {domain}. Service: {s['name']}. Responsibility & Scenarios: {s['role']}. Region: {s.get('region', 'Berlin')}."
            catalog.append({
                "domain": domain,
                "name": s["name"],
                "role": s["role"],
                "official_link": s["official_link"],
                "is_free": s.get("is_free", True),
                "region": s.get("region", "Berlin"),
                "text": text,
            })
    return catalog


def index_services_if_needed(force: bool = False) -> list[dict]:
    """Ensure all 24 services have pre-computed embeddings saved locally."""
    if not force and CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) == 24 and "embedding" in data[0]:
                    return data
        except Exception:
            pass

    client = _get_gemini_client()
    catalog = build_service_catalog()

    if client:
        try:
            # Gemini batch embedding (up to 100 texts at once)
            texts = [c["text"] for c in catalog]
            resp = client.models.embed_content(
                model="gemini-embedding-001",
                contents=texts,
            )
            for item, emb in zip(catalog, resp.embeddings):
                item["embedding"] = emb.values

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2)
            return catalog
        except Exception as e:
            print(f"[VectorSearch] Gemini embedding failed: {e}. Falling back to keyword search.")

    return catalog


def search_similar_services(query: str, top_k: int = 3) -> list[dict]:
    """
    Search services by semantic similarity to the citizen's query.
    Returns list of dicts with service details + 'similarity_score' (0.0 to 1.0).
    """
    catalog = index_services_if_needed()
    client = _get_gemini_client()

    if client and catalog and "embedding" in catalog[0]:
        try:
            resp = client.models.embed_content(
                model="gemini-embedding-001",
                contents=query,
            )
            query_emb = resp.embeddings[0].values
            
            scored = []
            for item in catalog:
                sim = _cosine_similarity(query_emb, item["embedding"])
                scored.append({**item, "similarity_score": round(sim, 4)})
            
            scored.sort(key=lambda x: x["similarity_score"], reverse=True)
            return scored[:top_k]
        except Exception as e:
            print(f"[VectorSearch] Query embedding error: {e}")

    # Fallback: simple token overlap / BM25 heuristic if offline
    tokens = set(query.lower().split())
    scored = []
    for item in catalog:
        item_tokens = set(item["text"].lower().split())
        overlap = len(tokens & item_tokens) / max(1, len(tokens))
        scored.append({**item, "similarity_score": round(overlap, 4)})
    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:top_k]
