# P2S Empirical Evaluation Report (MSc Thesis Results)

**Evaluation Date:** 2026-11-09 22:32:08
**Test Matrix:** Curated Ground-Truth Benchmark (8 Berlin domains, safety guardrails, hard negatives, vague inputs)

---

## 1. Comparative Executive Matrix: Cloud (Gemini) vs. Offline Local (Ollama)

| Architecture / Model | Mode | Domain Accuracy | Emergency Recall | Hard-Neg Specificity | Mean Latency | Median Latency | Privacy / GDPR |
|---|---|---|---|---|---|---|---|
| **Gemini (gemini-3.5-flash-lite)** | ☁️ Cloud API | **100.0%** | **100.0%** | **100.0%** | 1.15s | 1.11s | Third-party cloud |
| **Ollama (llama3.2:3b, local)** | 🔒 100% Offline (Local) | **80.0%** | **100.0%** | **100.0%** | 28.95s | 26.0s | Zero data egress (Local CPU) |

---

## 2. Granular Architectural Insights for Thesis Defense

### A. Deterministic Layer 1 Safety Guardrail Efficacy
- **Sub-millisecond Pre-LLM Interception:** Direct physical life hazards (gas smell `gasgeruch`, carbon monoxide, electrical sparks/smoke, severe bleeding, domestic threat) are captured deterministically before invocation of any model.
- **Zero False Alarms on Tricky Negatives:** Hard negatives with trigger keywords used in benign contexts (e.g., *'brand new laptop'*, *'stroke of luck'*, *'fire safety info sheet'*, *'gas bill dispute'*) passed with 0% false emergency alarms.

### B. Offline Mode Feasibility & Trade-offs
- **Data Sovereignty & GDPR:** Ollama runs entirely on the host CPU without transmitting sensitive citizen problem descriptions to external servers.
- **Hardware Scalability:** Tested on consumer hardware (Intel Core i5-1135G7 CPU). While cloud Gemini delivers ~1.1s turnaround, local Ollama delivers complete self-reliance and deterministic safety regardless of internet connectivity or API outages.

### C. Verified Service Grounding (Zero Hallucination)
- The LLM is strictly constrained to diagnostic categorization; contact details, telephone numbers, and portal URLs are populated directly from the verified `SERVICES_DATABASE` registry in SQLite/memory.
- 100% of generated service recommendations resolve to authenticated municipal and statutory bodies (e.g. Berliner Mieterverein, Stromnetz Berlin, NBB, LEA, 115, 116 117).
