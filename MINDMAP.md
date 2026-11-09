# P2S System — Architectural Mind Map

This mind map outlines the core pillars of the **P2S (Problem-to-Service)** system architecture for the MSc Computer Science Thesis.

```mermaid
mindmap
  root((P2S Triage Engine))
    1. Interaction Layer
      Web Speech API Dictation
      Bilingual Engine EN and DE
      Official PDF Referral Export
      Unstructured Complaint Input
    2. Triage & Guardrails
      Sub-millisecond Regex Interceptor 112 110
      Constrained LLM Gemini 3.5 Flash Lite
      Semantic Confidence Scoring
      Clarification State Machine
    3. Knowledge Grounding
      Facility & Building Emergencies
      Tenancy & Housing Law BMV DMB
      Health & Medical Care 116 117
      Bureaucracy & Immigration LEA 115
      Utilities & Energy Stromnetz BWB
      Consumer Rights & Fraud VZ Berlin
      IT Telecom & Handwerk HWK
    4. Empirical Evaluation
      95.2 Percent Domain Accuracy
      100 Percent Emergency Recall
      1.12 Seconds Average Latency
      21 Ground-Truth Scenarios
      Zero Contact Hallucinations
    5. Infrastructure & Data
      FastAPI Python 3 Async Backend
      SQLite Embedded Database
      Chart.js Live Dashboard
      Privacy-First Local Storage
```

---

## Interactive Local Mind Map
You can also view the styled interactive diagram locally by opening [`mindmap.html`](mindmap.html) in any browser, or use the **"Print / Save as PDF"** button inside it to export an executive summary sheet.
