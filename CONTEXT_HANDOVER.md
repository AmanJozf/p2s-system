# P2S (Problem-to-Service) — Project Context & Handover

## 1. Candidate & Academic Profile
* **Student:** Aman John Joseph
* **Degree:** MSc Computer Science
* **Student ID:** `BC012026MCS036`
* **Institution:** Berlin College of Business and Technology (BCBT) / Università degli Studi Guglielmo Marconi
* **Thesis Supervisor:** Prof. Pezhman Asadi (`pezhman.asadi@berlincollege.de`)
* **Project Name:** Problem-to-Service (P2S) — Berlin Citizen Triage System

---

## 2. Infrastructure & Live Links
* **Local Workspace Directory:** `C:\Users\91773\Desktop\Aman-Individual-Project-Proposals\p2s-system`
* **GitHub Repository:** [https://github.com/AmanJozf/p2s-system](https://github.com/AmanJozf/p2s-system) (Branch: `main`)
* **Live Production URL (Vercel):** [https://p2s-system.vercel.app](https://p2s-system.vercel.app)
* **Vercel Dashboard:** [https://vercel.com/aman-jozf/p2s-system](https://vercel.com/aman-jozf/p2s-system)
* **Live Routes:**
  * Landing Page: `https://p2s-system.vercel.app/`
  * Baseline Triage: `https://p2s-system.vercel.app/triage`
  * Apple Style Preview: `https://p2s-system.vercel.app/preview`
  * Service Directory: `https://p2s-system.vercel.app/services`
  * Analytics Dashboard: `https://p2s-system.vercel.app/dashboard`
  * About: `https://p2s-system.vercel.app/about`

---

## 3. Architecture & Tech Stack
* **Backend:** Python 3.11+, FastAPI (`main.py`)
* **Deployment:** Vercel Serverless (`@vercel/python`, `maxDuration: 30s` via `vercel.json`)
* **Database:** SQLite (`backend/database.py` with automatic fallback to `/tmp/p2s_data.db` on Vercel)
* **LLM Engine:** Dual-provider architecture (`backend/llm_providers.py`):
  * **Cloud Primary:** Gemini API (`gemini-3.5-flash` with zero-wait instant failover to `gemini-3.5-flash-lite` to prevent 503 traffic spikes)
  * **Edge / Offline:** Ollama (`llama3.2:3b`)
* **Emergency Safety Guardrails:** Deterministic regex pre-filters for immediate life-safety hazards (112, 110, NBB Gas Emergency) bypassing LLM latency.
* **Bilingual Support:** Full English (EN) and German (DE) localization.

---

## 4. Current File Structure
```
p2s-system/
├── backend/
│   ├── database.py         # SQLite database handler (serverless /tmp aware)
│   ├── knowledge_base.py   # Verified Berlin statutory bodies & emergency directory
│   ├── llm_providers.py    # Resilient Gemini & Ollama clients with 503 failover
│   ├── schemas.py          # Pydantic models for triage requests & responses
│   └── triage_engine.py    # Regex safety guardrails + hybrid classification logic
├── docs/
│   ├── P2S_Thesis_Topic_Sheet.pdf  # Compiled 1-page topic proposal sent to Prof. Asadi
│   └── THESIS_TOPIC_SHEET.md       # Markdown source of the 10-point topic sheet
├── frontend/
│   ├── index.html          # Main landing page
│   ├── triage.html         # Working baseline 3-step triage wizard (DO NOT BREAK)
│   ├── preview.html        # Apple-inspired aesthetic sandbox
│   ├── services.html       # Public services directory
│   ├── dashboard.html      # Stats & charts
│   ├── about.html          # Academic project info
│   └── static/
│       ├── nav.js          # Shared navbar, language switcher & scenario chips
│       └── style.css       # Core styling variables
├── main.py                 # FastAPI application routes (/api/triage, /api/triage/start)
├── requirements.txt        # fastapi, uvicorn, pydantic, google-genai, python-dotenv, httpx
└── vercel.json             # Vercel serverless deployment config
```

---

## 5. Ongoing Task for the New Chat
* **Primary Objective:** Redesign and polish the visual style of `frontend/preview.html` (e.g. Apple light/dark, Stripe-style, Linear precision, or customized UI).
* **Golden Rules:**
  1. **Do NOT break or overwrite the working baseline `frontend/triage.html`.** All styling experiments happen in `frontend/preview.html` or new preview templates.
  2. Any changes pushed to `origin main` auto-deploy to [https://p2s-system.vercel.app](https://p2s-system.vercel.app) within ~15 seconds.
  3. No AI slop (avoid arbitrary purple gradients or floating blobs; maintain clean contrast, authentic typography, and WCAG AA accessibility).
