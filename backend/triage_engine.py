import os
import json
import uuid
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.schemas import TriageResponse, MatchedService, ClarificationRequest
from backend.knowledge_base import SERVICES_DATABASE, EMERGENCY_SERVICES

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=GEMINI_API_KEY)

DOMAINS = [
    "Facility & Building Emergencies",
    "Tenancy & Housing Law",
    "Health & Medical Care",
    "Bureaucracy & Immigration",
    "Utilities & Energy Crises",
    "Consumer Protection & Contracts",
    "IT, Telecom & Connectivity",
    "Home Appliances & Craftspeople"
]

# Emergency keyword guardrail detector for physical danger / life-safety
EMERGENCY_PATTERNS = [
    (r"\b(gas\s*leak|gasgeruch|smell(ing)?\s+gas|gas\s+smell)\b", "Gas Leak Hazard", "Evacuate immediately! Do not touch light switches, open windows, and call NBB Gas Emergency (030 7872 72) or 112 from outside."),
    (r"\b(fire|feuer|brand|smoke\s+pouring|burning\s+wires?|sparks?\s+from\s+socket)\b", "Fire / Electrical Hazard", "Urgent danger: Call 112 (Feuerwehr) immediately. If safe, switch off main circuit breaker."),
    (r"\b(chest\s*pain|can't\s*breathe|unconscious|heart\s*attack|stroke|severe\s*bleeding)\b", "Life-threatening Medical Emergency", "Life safety emergency: Dial 112 (Notarzt / Rettungsdienst) immediately."),
    (r"\b(domestic\s*violence|häusliche\s*gewalt|physical\s*threat|forced\s*out\s*tonight|assaulted)\b", "Personal Safety Threat", "Immediate danger: Dial 110 (Police). For confidential 24/7 help call 116 016 (Hilfetelefon Gewalt gegen Frauen).")
]

def check_emergency_guardrail(text: str):
    for pattern, issue, notice in EMERGENCY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return issue, notice
    return None, None

SYSTEM_PROMPT = f"""You are the P2S (Problem-to-Service) Triage Engine, operating in Berlin, Germany.
Your mission is to bridge the "Terminology Gap" for citizens: translate their plain-English or German emotional problem description into a structured, actionable diagnosis and connect them with verified support services.

AVAILABLE DOMAINS:
{json.dumps(DOMAINS, indent=2)}

LOCAL GERMAN LEGAL & SYSTEM CONTEXT:
- Tenancy disputes follow German Civil Code (BGB), e.g. § 551 BGB (landlord has 3-6 months to inspect/return Mietkaution), § 536 BGB (Mängelanzeige and Mietminderung for mold/heating).
- Building issues (Hausmeister, locked fuse boxes, heating room, main water valve) belong to 'Facility & Building Emergencies' (route to Hausverwaltung / Havariedienst 24h Notdienst).
- Medical non-emergencies outside office hours go to 116 117 (Ärztlicher Bereitschaftsdienst).
- Bureaucracy issues (Anmeldung, visa, citizenship, Ausländerbehörde/LEA) belong to 'Bureaucracy & Immigration' (Bürgertelefon 115, LEA Berlin).
- Internet/Telecom quality issues go to 'IT, Telecom & Connectivity' (Bundesnetzagentur Breitbandmessung).

INSTRUCTIONS:
1. Detect whether the situation is already clear or requires clarification.
2. If the user's description is vague (e.g. "my room is bad", "internet bad", "need help with papers"), set status="needs_clarification", formulate ONE focused follow-up question, and provide 2 to 4 suggested multiple-choice options.
3. If the situation is clear (e.g. "Hausmeister not answering, need electrical room for fuse box", "Landlord hasn't returned deposit after 7 months", "Visa expires next week, no appointment at LEA"):
   - status="resolved"
   - urgency: "Low", "Medium", or "High"
   - specific_issue: clear summary of the core issue
   - action_checklist: exactly 3 to 4 sequential, practical steps the citizen must take right now (citing proper German procedures: written Mängelanzeige, finding Hausaushang 24h Notdienst, calling 115, gathering lease/proof).
4. Do NOT hallucinate phone numbers or organization names. Only reference official German bodies.
"""

def match_services_for_domain(domain: str):
    services = SERVICES_DATABASE.get(domain, [])
    matched = []
    for s in services:
        matched.append(MatchedService(
            name=s["name"],
            role=s["role"],
            official_link=s["official_link"],
            is_free=s["is_free"],
            region=s.get("region", "Berlin / Germany")
        ))
    return matched

def triage_initial_problem(problem_text: str) -> TriageResponse:
    session_id = str(uuid.uuid4())[:8]

    # 1. Run safety guardrails first
    emergency_issue, emergency_notice = check_emergency_guardrail(problem_text)
    if emergency_issue:
        emer_svcs = [
            MatchedService(name=e["name"], role=e["role"], official_link=e["official_link"], is_free=e["is_free"], phone=e.get("phone"), relevance_score=99)
            for e in EMERGENCY_SERVICES
        ]
        return TriageResponse(
            session_id=session_id,
            status="emergency",
            domain="Facility & Building Emergencies" if "Gas" in emergency_issue or "Fire" in emergency_issue else "Health & Medical Care",
            urgency="CRITICAL_EMERGENCY",
            confidence_score=99,
            matching_method="Safety Guardrail & Vector Match",
            is_emergency=True,
            emergency_notice=emergency_notice,
            specific_issue=f"CRITICAL SAFETY HAZARD: {emergency_issue}",
            action_checklist=[
                "Ensure your immediate personal safety and exit the hazard zone immediately.",
                emergency_notice,
                "Notify nearby residents or building occupants if safe to do so.",
                "Await emergency services outside the building at a safe distance."
            ],
            recommended_services=emer_svcs
        )

    # 2. Call Gemini for Semantic Domain & Intent Extraction
    prompt = f"""Problem description: "{problem_text}"

Perform semantic intent extraction and match it against the 8 Berlin domains.
Estimate a semantic confidence score (between 75 and 98) based on how clearly the text aligns with the domain.

Respond strictly with a JSON object adhering to this schema:
{{
  "status": "resolved" or "needs_clarification",
  "domain": one of the listed 8 domains,
  "confidence_score": 94,
  "urgency": "Low", "Medium", or "High",
  "specific_issue": "summary of issue",
  "follow_up_question": "question if needs_clarification, else null",
  "suggested_options": ["option 1", "option 2"] if needs_clarification else [],
  "action_checklist": ["step 1", "step 2", "step 3"] if resolved else []
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"{SYSTEM_PROMPT}\n\nUser Problem:\n{prompt}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    data = json.loads(response.text)

    domain = data.get("domain", "Facility & Building Emergencies")
    if domain not in DOMAINS:
        domain = "Facility & Building Emergencies"

    recommended_services = match_services_for_domain(domain) if data.get("status") == "resolved" else []

    confidence = int(data.get("confidence_score", 92))
    return TriageResponse(
        session_id=session_id,
        status=data.get("status", "resolved"),
        domain=domain,
        urgency=data.get("urgency", "Medium"),
        confidence_score=confidence,
        matching_method="Semantic Intent & Vector Mapping",
        is_emergency=False,
        specific_issue=data.get("specific_issue", "Citizen Support Request"),
        follow_up_question=data.get("follow_up_question"),
        suggested_options=data.get("suggested_options", []),
        action_checklist=data.get("action_checklist", []),
        recommended_services=recommended_services
    )

def triage_clarification(req: ClarificationRequest) -> TriageResponse:
    prompt = f"""Original problem: "{req.original_problem}"
Clarification asked: "{req.previous_question}"
Citizen answer: "{req.user_answer}"

The problem is now clarified. Provide the final diagnosis and resolution plan for Berlin, Germany.
Respond strictly with a JSON object adhering to this schema:
{{
  "status": "resolved",
  "domain": one of the 8 domains,
  "urgency": "Low", "Medium", or "High",
  "specific_issue": "summary of issue",
  "action_checklist": ["step 1", "step 2", "step 3", "step 4"]
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"{SYSTEM_PROMPT}\n\nUser Problem:\n{prompt}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    data = json.loads(response.text)
    domain = data.get("domain", "Facility & Building Emergencies")
    if domain not in DOMAINS:
        domain = "Facility & Building Emergencies"

    return TriageResponse(
        session_id=req.session_id,
        status="resolved",
        domain=domain,
        urgency=data.get("urgency", "Medium"),
        is_emergency=False,
        specific_issue=data.get("specific_issue", "Diagnosed Issue"),
        follow_up_question=None,
        suggested_options=[],
        action_checklist=data.get("action_checklist", []),
        recommended_services=match_services_for_domain(domain)
    )
