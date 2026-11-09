# P2S — Problem to Service (Berlin Edition 🇩🇪)

> **AI-Powered Public Service Triage & Routing System**  
> *MSc Computer Science Thesis Project*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/AmanJozf/p2s-system)
[![Accuracy](https://img.shields.io/badge/Benchmark_Accuracy-95.2%25-blueviolet.svg)](docs/EVALUATION_REPORT.md)

---

## 📌 Executive Summary

Ordinary citizens and students facing real-life emergencies often experience the **"Terminology Gap"**:
* People describe their distress in unstructured, emotional language (*"my landlord stole my deposit"*, *"boiler is leaking cold water"*, *"visa expires in 10 days"*).
* Bureaucracies and public services hide behind complex legalistic jargon (*"§ 551 BGB Tenancy Deposit Adjudication"*, *"Havariedienst Notdienst"*, *"Breitbandmessung"*).

**P2S (Problem-to-Service)** is an intelligent triage engine that translates raw, unstructured human complaints into an immediate **4-step action checklist** and routes citizens directly to **verified public authorities, emergency helplines, and tenant associations** in under 2 seconds.

---

## 🏛️ System Architecture & Workflow

```text
Citizen Input (Text / Voice Dictation in EN or DE)
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Deterministic Safety Guardrails            │
│  (Sub-millisecond regex interceptor for 112/110 hazards) │
└───────────────────────────┬─────────────────────────────┘
                            │ (If safe)
                            ▼
┌─────────────────────────────────────────────────────────┐
│               Constrained LLM Triage Engine             │
│        (Google Gemini 3.5 Flash Lite / Structured JSON)  │
│                                                         │
│   • Semantic Intent Extraction                          │
│   • Ambiguity Clarification State Machine               │
│   • Real-Time Confidence Scoring (%)                    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│             Verified Knowledge Grounding (RAG)          │
│    (28 Verified Berlin & German Authorities / Zero 404s)│
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
     Action Plan + Referral Sheet + Official PDF Export
```

---

## 📂 8 Supported Life Domains (Berlin Reference Region)

1. **🏢 Facility & Building Emergencies:** Unresponsive Hausmeister, locked fuse boxes, boiler failures, 24h Havariedienst.
2. **🏠 Tenancy & Housing Law:** Withheld Kaution deposits (§ 551 BGB), mold Mietminderung (§ 536 BGB), Berliner Mieterverein (BMV).
3. **🏥 Health & Medical Care:** Out-of-hours on-call doctors (**116 117**), emergency pharmacies, Berliner Krisendienst.
4. **🏛️ Bureaucracy & Immigration:** Student visa extensions (LEA Berlin), Bürgeramt appointments, Citizen Hotline (**115**).
5. **⚡ Utilities & Grid Crises:** Stromnetz Berlin power outages, Berliner Wasserbetriebe (BWB), Gasnotruf (**030 7872 72**).
6. **🛡️ Consumer Protection & Contracts:** Gym subscription traps, debt collection defense (Inkasso), Verbraucherzentrale Berlin.
7. **💻 IT, Telecom & Connectivity:** Bundesnetzagentur Broadband Speed Test (Breitbandmessung), ISP contract cancellation.
8. **🔧 Home Appliances & Craftspeople:** Certified emergency plumbers, Handwerkskammer (HWK) Berlin electricians.

---

## 📊 Empirical Evaluation Results

The system was evaluated against a ground-truth benchmark suite of 21 complex real-world scenarios across all 8 domains (`evaluate.py`).

| Performance Metric | Measured Result | Benchmark Standard | Status |
|---|---|---|---|
| **Domain Classification Accuracy** | **95.2%** (20 / 21) | Target: >90% | **EXCEEDED** |
| **Emergency Safety Recall** | **100.0%** (3 / 3) | Target: 100% | **OPTIMAL** |
| **Mean Response Latency** | **1.12 seconds** | Target: <4.0s | **OPTIMAL** |
| **Safety Interception Latency** | **<0.01 seconds** | Deterministic | **SUB-MILLISECOND** |
| **Contact Hallucination Rate** | **0.0%** | Zero fake contacts | **GUARANTEED** |

Full metrics available in [`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md) and [`docs/evaluation_results.csv`](docs/evaluation_results.csv).  
Visual system architecture: [`docs/MINDMAP.md`](docs/MINDMAP.md).

---

## ✨ Key Features

* **🌐 Full 7-Page Web Application:** Home, Triage Tool, Verified Services Directory, Analytics Dashboard (Chart.js), Local Session History, System Architecture, and Admin Panel.
* **🇩🇪 / 🇬🇧 Bilingual Switcher:** Real-time toggle between German (`DE`) and English (`EN`).
* **🎙️ Client-Side Voice Dictation:** Microphone speech-to-text powered by the native browser Web Speech API.
* **📄 Official Case Referral PDF Export:** One-click export to printable official case documentation for landlords or municipal offices.
* **🔒 Privacy-First Architecture:** Embedded SQLite (`p2s_data.db`) for local session analytics without external database daemons.

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/AmanJozf/p2s-system.git
cd p2s-system
```

### 2. Install dependencies
```bash
pip install fastapi uvicorn google-genai pydantic python-dotenv
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
LLM_PROVIDER=gemini
```

### 4. Run the server
```bash
python -m uvicorn main:app --reload --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 🧪 Running the Benchmark Evaluation

To reproduce the academic evaluation results locally:
```bash
python evaluate.py
```
This executes the automated test suite and updates `EVALUATION_REPORT.md` and `evaluation_results.csv`.
