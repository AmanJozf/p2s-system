# Problem-to-Service (P2S): Evaluating Dual-Mode LLM Intent Triage and Grounded Retrieval for Municipal Public Services

**Candidate:** Aman John Joseph (Student ID: BC012026MCS036)  
**Degree:** Master of Science in Computer Science  
**Institution:** Berlin College of Business and Technology (BCBT) / Università degli Studi Guglielmo Marconi  
**Supervisor:** Prof. Pezhman Asadi  
**Date:** November 2026  

---

### 1. Project Context & Motivation
Public administration services and civil advice bodies in Germany operate behind specialized bureaucratic terminology (e.g., *§ 551 BGB Mietkaution*, *Havariedienst*, *Bürgeramt Zuständigkeitsfinder*). Everyday citizens and international residents describe emergencies and distress in unstructured, colloquial language (*"my landlord won't return my deposit"*, *"water leaking through the ceiling"*). This disconnect—the **terminology gap**—leads to delayed responses, misdirected emergency calls, and administrative overload.

This research extends the working prototype developed during the **Individual Project (P2S)**. While the initial project established the technical foundation—an asynchronous FastAPI service with a bilingual (EN/DE) interface and deterministic emergency guardrails—this thesis investigates the underlying empirical and architectural questions: evaluating the accuracy, latency, safety, and data sovereignty trade-offs between commercial cloud APIs and privacy-preserving local edge models.

---

### 2. Research Questions
* **Primary Question:** How effectively can a hybrid LLM triage pipeline classify unstructured citizen problem descriptions and route them to verified public services in Berlin, compared with traditional keyword-based matching?
* **Sub-Questions:**
  1. *Emergency Guardrails:* How reliably can rule-based pre-filters intercept critical life-safety hazards (such as gas leaks or medical emergencies) compared to relying on LLM classification alone?
  2. *Cloud vs. Local Edge Performance:* What are the measurable trade-offs in categorization accuracy, response latency, and citizen data privacy when comparing cloud APIs (Gemini) with lightweight offline models (Ollama) running locally?
  3. *Hallucination Mitigation:* How effectively does grounding LLM outputs in a verified municipal database eliminate fabricated contact details and outdated administrative procedures?

---

### 3. Aims & Objectives
* **Aim:** To design, benchmark, and evaluate a privacy-conscious, bilingual citizen triage system that reliably bridges colloquial distress narratives with verified public support infrastructure.
* **Key Objectives:**
  1. Develop a production-ready dual-provider triage engine supporting both cloud APIs and offline local LLMs.
  2. Curate an empirical benchmark dataset of 70 realistic, bilingual citizen problem scenarios across 8 Berlin municipal domains, complete with hard negative controls.
  3. Execute automated comparative evaluations measuring domain accuracy, safety recall, and response latency across model configurations.
  4. Formulate architectural recommendations for deploying privacy-compliant AI triage within public sector and civic tech workflows.

---

### 4. Proposed Contribution
* **Hybrid Triage Architecture:** Demonstrating that high-stakes civic triage requires rule-based pre-filters for life-safety hazards rather than relying on prompt instructions alone.
* **Empirical Cloud vs. Edge Benchmark:** Delivering real-world benchmark data on whether small quantized edge models (3B parameters) running locally on consumer hardware can meet municipal safety and categorization standards under strict GDPR constraints.
* **Grounded Civic Routing:** A proven pipeline that prevents generative hallucinations by strictly binding classification outputs to authenticated regional services.

---

### 5. Methodology & System Design
The system follows a three-stage pipeline implemented in Python and FastAPI:
1. **Deterministic Guardrail Layer:** Raw incoming text is parsed via compiled regex matchers targeting high-consequence life/safety events (gas leaks, fire, medical trauma). If triggered, the system returns immediate emergency protocols (112/110) in under 1ms.
2. **LLM Intent Classification:** Non-emergency requests pass to the active model provider (Cloud Gemini via REST or Local Ollama via HTTP). The model extracts intent, identifies ambiguity, and returns structured JSON conforming to strict Pydantic schemas.
3. **Registry Grounding:** Diagnostic outputs are mapped against an embedded SQLite knowledge base containing verified Berlin authorities (e.g., Berliner Mieterverein, Stromnetz Berlin, LEA, 115, 116 117), returning structured 4-step action plans and verified links.

---

### 6. Evaluation Framework & Preliminary Results
The system is evaluated using an automated test harness (`evaluate.py`) against a curated 70-scenario ground-truth matrix covering 8 domains: Facility Emergencies, Tenancy Law, Healthcare, Immigration/Bureaucracy, Utilities, Consumer Rights, Handwerk, and Emergency Hazards.

| Metric | Cloud API (Gemini 3.5 Flash Lite) | Local Edge (Ollama Llama 3.2:3b) | Rule Baseline (Regex) | Target Standard |
| :--- | :--- | :--- | :--- | :--- |
| **Domain Classification Accuracy** | **100.0%** | **80.0%** | 48.0% | ≥ 80.0% |
| **Emergency Safety Recall** | **100.0%** | **100.0%** | 85.0% | **100.0%** |
| **Hard-Negative Specificity** | **100.0%** | **100.0%** | 62.0% | ≥ 95.0% |
| **Mean Interactive Latency** | **1.15s** | **28.95s (CPU)** | < 0.01s | < 3s (Cloud) / < 30s (Edge) |
| **Data Sovereignty (GDPR)** | Cloud data transfer | **100% Local (Zero egress)** | 100% Local | Compliant with EU Art. 9 |

---

### 7. Key References
1. Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 2020.
2. Touvron, H., et al. (2023). *Llama 2: Open Foundation and Fine-Tuned Chat Models.* arXiv:2307.09288.
3. Ji, Z., et al. (2023). *Survey of Hallucination in Natural Language Generation.* ACM Computing Surveys, 55(12).
4. Alizadeh, K., et al. (2024). *LLM in a flash: Efficient Large Language Model Inference with Limited Memory.* IEEE/ACM Trans. Networking.
5. Senatskanzlei Berlin (2024). *Standardisierung von Bürgerdienstleistungen und Zuständigkeitsfinder (115).*

---

### 8. Scope & Risk Management
* **In Scope:** Administrative and civil routing for Berlin-based residents across 8 life domains; comparative benchmarking of cloud vs. local inference; safety guardrails; bilingual support (EN/DE).
* **Out of Scope:** Rendering legal representation or direct integration into closed municipal dispatch backends.
* **Risk & Mitigation:** Local edge models on CPU can suffer from latency bottlenecks; this is addressed through asynchronous task handling, streaming responses, and pre-computed embedding caches.
