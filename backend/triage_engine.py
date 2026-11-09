import re
import uuid

from backend.schemas import TriageResponse, MatchedService, ClarificationRequest
from backend.knowledge_base import SERVICES_DATABASE, EMERGENCY_SERVICES
from backend.llm_providers import get_provider

DOMAINS = [
    "Facility & Building Emergencies",
    "Tenancy & Housing Law",
    "Health & Medical Care",
    "Bureaucracy & Immigration",
    "Utilities & Energy Crises",
    "Consumer Protection & Contracts",
    "IT, Telecom & Connectivity",
    "Home Appliances & Craftspeople",
]

FACILITY = "Facility & Building Emergencies"
HEALTH = "Health & Medical Care"

# --- Layer 1: deterministic safety guardrail ---------------------------------
# Patterns are phrase-level (not bare words) to avoid false alarms such as
# "brand new laptop" or "fire safety inspection".
_F = re.IGNORECASE | re.UNICODE
EMERGENCY_PATTERNS = [
    (re.compile(r"\b(gas\s*leak\w*|gas\s+smell\w*|smell(?:s|ing|ed)?\s+(?:of\s+)?gas|gas\s+(?:is\s+)?leaking|gasgeruch|gasaustritt|rieche\s+gas|riecht\s+(?:es\s+)?nach\s+gas|gas\s*geruch)\b", _F),
     "Gas Leak Hazard", FACILITY,
     "Evacuate immediately! Do not touch light switches or flames, open windows on your way out, and call the NBB gas emergency line (030 7872 72) or 112 from outside."),
    (re.compile(r"\b(carbon\s+monoxide|kohlenmonoxid|co[\s-]+(?:alarm|detector|melder|warner))\b", _F),
     "Carbon Monoxide Hazard", FACILITY,
     "Leave the building now, open doors and windows on the way out, and call 112 from outside. Do not go back in."),
    (re.compile(r"\b(on\s+fire|caught\s+fire|catching\s+fire|fire\s+broke\s+out|(?:house|flat|apartment|building|kitchen)\s+fire|smoke\s+(?:is\s+|are\s+)?(?:pouring|coming)|sparks?\s+and\s+smoke|burning\s+(?:smell|wires?|cables?)|sparks?\s+(?:from|coming\s+from|flying)|es\s+brennt|wohnungsbrand|kabelbrand|brandgeruch|rauchentwicklung|funken\s+aus|electric(?:al)?\s+shock|electrocut\w*|stromschlag)\b", _F),
     "Fire / Electrical Hazard", FACILITY,
     "Urgent danger: call 112 (Feuerwehr) immediately. If it is safe, switch off the main circuit breaker and leave the building."),
    (re.compile(r"\b(chest\s+pain|(?:can'?t|cannot|not)\s+breath\w*|difficulty\s+breathing|unconscious|unresponsive|(?:had|having|suffered|suspected|possible)\s+(?:a\s+)?stroke(?!\s+of)|heart\s+attack|severe(?:ly)?\s+bleeding|bleeding\s+heavily|overdos(?:e|ed)|seizure|anaphyla\w+|(?:someone|he|she|roommate|friend|neighbou?r|partner|mother|father|mum|dad)\s+(?:has\s+|just\s+)?collapsed|brustschmerz\w*|herzinfarkt|schlaganfall|bewusstlos\w*|atemnot|keine\s+luft|starke\s+blutung|überdosis|krampfanfall)\b", _F),
     "Life-threatening Medical Emergency", HEALTH,
     "Life-safety emergency: dial 112 (Notarzt / Rettungsdienst) immediately and stay on the line."),
    (re.compile(r"\b(suicid\w*|kill\s+myself|end(?:ing)?\s+my\s+life|want\s+to\s+die|selbstmord|suizid\w*|mich\s+umbringen)\b", _F),
     "Acute Mental-Health Crisis", HEALTH,
     "You are not alone. If you are in immediate danger call 112. Free, confidential 24/7 support: TelefonSeelsorge 0800 111 0 111 or the Berliner Krisendienst."),
    (re.compile(r"\b(domestic\s+violence|häusliche\s+gewalt|(?:being|was|got|been)\s+(?:attacked|assaulted|threatened)|threaten\w*\s+(?:to\s+)?(?:kill|hurt|hit)\s+me|(?:hitting|beating)\s+me|bedroht\w*|schlägt\s+mich|forced\s+out\s+tonight)\b", _F),
     "Personal Safety Threat", HEALTH,
     "Immediate danger: dial 110 (Police). For confidential 24/7 help call 116 016 (Hilfetelefon Gewalt gegen Frauen)."),
]


def check_emergency_guardrail(text: str):
    """Return (issue, notice, domain) for the first matching hazard, else (None, None, None)."""
    for pattern, issue, domain, notice in ((p, i, d, n) for p, i, d, n in EMERGENCY_PATTERNS):
        if pattern.search(text):
            return issue, notice, domain
    return None, None, None


def _emergency_response(session_id, issue, notice, domain, method, provider) -> TriageResponse:
    services = [
        MatchedService(name=e["name"], role=e["role"], official_link=e["official_link"],
                       is_free=e["is_free"], phone=e.get("phone"), relevance_score=99)
        for e in EMERGENCY_SERVICES
    ]
    return TriageResponse(
        session_id=session_id,
        status="emergency",
        domain=domain,
        urgency="CRITICAL_EMERGENCY",
        confidence_score=99,
        matching_method=method,
        provider=provider,
        is_emergency=True,
        emergency_notice=notice,
        specific_issue=f"CRITICAL SAFETY HAZARD: {issue}",
        action_checklist=[
            "Ensure your immediate personal safety and move away from the hazard.",
            notice,
            "Warn other people nearby if it is safe to do so.",
            "Wait for emergency services at a safe distance.",
        ],
        recommended_services=services,
    )


SYSTEM_PROMPT = f"""You are the P2S (Problem-to-Service) Triage Engine for Berlin, Germany.
You translate a citizen's plain-language problem (English or German) into a structured diagnosis. Write every free-text field in the SAME language the citizen used.

DOMAINS (choose exactly one):
{chr(10).join('- ' + d for d in DOMAINS)}

ROUTING RULES:
- {FACILITY}: problems INSIDE the building the landlord/Hausverwaltung controls: Hausmeister unreachable, locked fuse/electrical/boiler room, burst pipe inside the building, broken entrance lock, stuck elevator, no heating in the whole building. Route to Hausverwaltung / Havariedienst (24h).
- Tenancy & Housing Law: deposit (Kaution, § 551 BGB), rent increases, Mietminderung / mold (§ 536 BGB), termination (Kündigung, Eigenbedarf), landlord entering without permission.
- Utilities & Energy Crises: street- or district-wide power cut, water or gas supply from the utility, energy bills and supplier disputes.
- Health & Medical Care: non-emergency medical needs, on-call doctor (116 117), emergency pharmacy, mental-health support.
- Bureaucracy & Immigration: Anmeldung, residence permit/visa, LEA, Bürgeramt, tax ID, blocked account paperwork.
- Consumer Protection & Contracts: subscriptions, gym contracts, debt collection (Inkasso), online shop disputes, flight compensation.
- IT, Telecom & Connectivity: internet speed or outage, router, ISP contract, broken laptop or phone.
- Home Appliances & Craftspeople: broken appliance (washing machine, fridge, oven), needing a certified electrician or plumber.

RULES:
1. If the message is too vague to pick a domain (e.g. "everything is broken", "I need help with papers"), set status="needs_clarification", ask ONE specific follow_up_question and give 2-4 suggested_options.
2. If it is clear, set status="resolved" with urgency Low/Medium/High, a one-sentence specific_issue and an action_checklist of 3-4 concrete steps using proper German procedures (written Mängelanzeige, Hausaushang with the 24h Notdienst number, Breitbandmessung, calling 115, ...).
3. confidence_score: integer 60-98 for how clearly the text matches the chosen domain; lower it when the case is borderline.
4. immediate_danger: true ONLY if someone's life or physical safety is at risk right now (gas/CO, fire, electrocution, medical emergency, violence, suicide risk). A broken appliance, a cut power line outage or an angry landlord is NOT immediate danger.
5. Never invent phone numbers or organisation names.
6. Reply with JSON only.
"""

_BASE_PROPS = {
    "domain": {"type": "string", "enum": DOMAINS},
    "confidence_score": {"type": "integer"},
    "urgency": {"type": "string", "enum": ["Low", "Medium", "High"]},
    "specific_issue": {"type": "string"},
    "immediate_danger": {"type": "boolean"},
    "action_checklist": {"type": "array", "items": {"type": "string"}},
}

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["resolved", "needs_clarification"]},
        **_BASE_PROPS,
        "follow_up_question": {"type": ["string", "null"]},
        "suggested_options": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "domain", "confidence_score", "urgency", "specific_issue",
                 "immediate_danger", "follow_up_question", "suggested_options", "action_checklist"],
}

CLARIFY_SCHEMA = {
    "type": "object",
    "properties": dict(_BASE_PROPS),
    "required": ["domain", "confidence_score", "urgency", "specific_issue",
                 "immediate_danger", "action_checklist"],
}


def match_services_for_domain(domain: str):
    return [
        MatchedService(
            name=s["name"],
            role=s["role"],
            official_link=s["official_link"],
            is_free=s["is_free"],
            region=s.get("region", "Berlin / Germany"),
        )
        for s in SERVICES_DATABASE.get(domain, [])
    ]


def _clean_domain(value) -> str:
    return value if value in DOMAINS else FACILITY


def _clean_confidence(value, default=85) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return default


def _llm_danger_response(session_id, data, provider) -> TriageResponse:
    return _emergency_response(
        session_id,
        issue=data.get("specific_issue") or "Possible immediate danger",
        notice="The assistant detected possible immediate danger. If anyone is in danger call 112 now (police: 110).",
        domain=_clean_domain(data.get("domain")),
        method="Safety check by language model (layer 2)",
        provider=provider.label,
    )


def triage_initial_problem(problem_text: str, provider_name: str | None = None) -> TriageResponse:
    session_id = str(uuid.uuid4())[:8]

    # Layer 1: deterministic guardrail, no model call, ~0 ms
    issue, notice, domain = check_emergency_guardrail(problem_text)
    if issue:
        return _emergency_response(session_id, issue, notice, domain,
                                   method="Safety guardrail (rule-based, layer 1)", provider="guardrail")

    # Layer 2 + classification: one LLM call (Gemini or Ollama, same interface)
    provider = get_provider(provider_name)
    prompt = f'Citizen message: "{problem_text}"\n\nRespond with the JSON object.'
    data = provider.generate_json(prompt, system=SYSTEM_PROMPT, schema=TRIAGE_SCHEMA)

    if data.get("immediate_danger") is True:
        return _llm_danger_response(session_id, data, provider)

    status = data.get("status") if data.get("status") in ("resolved", "needs_clarification") else "resolved"
    domain = _clean_domain(data.get("domain"))

    return TriageResponse(
        session_id=session_id,
        status=status,
        domain=domain,
        urgency=data.get("urgency", "Medium"),
        confidence_score=_clean_confidence(data.get("confidence_score")),
        matching_method="LLM intent classification + verified service lookup",
        provider=provider.label,
        is_emergency=False,
        specific_issue=data.get("specific_issue", "Citizen Support Request"),
        follow_up_question=data.get("follow_up_question") if status == "needs_clarification" else None,
        suggested_options=data.get("suggested_options", []) if status == "needs_clarification" else [],
        action_checklist=data.get("action_checklist", []) if status == "resolved" else [],
        recommended_services=match_services_for_domain(domain) if status == "resolved" else [],
    )


def triage_clarification(req: ClarificationRequest, provider_name: str | None = None) -> TriageResponse:
    # The clarification answer can reveal danger too ("...and I can smell gas now")
    issue, notice, g_domain = check_emergency_guardrail(f"{req.original_problem} {req.user_answer}")
    if issue:
        return _emergency_response(req.session_id, issue, notice, g_domain,
                                   method="Safety guardrail (rule-based, layer 1)", provider="guardrail")

    provider = get_provider(provider_name)
    prompt = (
        f'Original message: "{req.original_problem}"\n'
        f'Clarifying question asked: "{req.previous_question}"\n'
        f'Citizen answer: "{req.user_answer}"\n\n'
        "The problem is now clarified. Give the final diagnosis and a 3-4 step plan as the JSON object."
    )
    data = provider.generate_json(prompt, system=SYSTEM_PROMPT, schema=CLARIFY_SCHEMA)

    if data.get("immediate_danger") is True:
        return _llm_danger_response(req.session_id, data, provider)

    domain = _clean_domain(data.get("domain"))
    return TriageResponse(
        session_id=req.session_id,
        status="resolved",
        domain=domain,
        urgency=data.get("urgency", "Medium"),
        confidence_score=_clean_confidence(data.get("confidence_score")),
        matching_method="LLM intent classification + verified service lookup",
        provider=provider.label,
        is_emergency=False,
        specific_issue=data.get("specific_issue", "Diagnosed Issue"),
        follow_up_question=None,
        suggested_options=[],
        action_checklist=data.get("action_checklist", []),
        recommended_services=match_services_for_domain(domain),
    )
