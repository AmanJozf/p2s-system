from pydantic import BaseModel, Field
from typing import List, Optional

class ProblemRequest(BaseModel):
    problem_description: str = Field(..., description="The user's raw problem description in plain everyday language.")

class ClarificationRequest(BaseModel):
    session_id: str
    original_problem: str
    previous_question: str
    user_answer: str

class MatchedService(BaseModel):
    name: str
    role: str
    official_link: str
    is_free: bool
    phone: Optional[str] = None
    region: Optional[str] = "Berlin / Germany"
    relevance_score: Optional[int] = Field(default=95, description="Semantic match relevance percentage")

class TriageResponse(BaseModel):
    session_id: str
    status: str = Field(..., description="'resolved', 'needs_clarification', or 'emergency'")
    domain: str = Field(..., description="Categorized problem domain")
    urgency: str = Field(..., description="Low, Medium, High, or CRITICAL_EMERGENCY")
    confidence_score: int = Field(default=94, description="Calculated semantic confidence match percentage")
    matching_method: str = Field(default="Semantic Vector Analysis", description="Retrieval method used")
    is_emergency: bool = Field(default=False, description="True if immediate life safety / physical danger hazard")
    emergency_notice: Optional[str] = Field(None, description="Clear emergency instruction (e.g. dial 112 / evacuate)")
    specific_issue: str = Field(..., description="Concise professional summary of the diagnosed issue")
    follow_up_question: Optional[str] = Field(None, description="A single targeted question if clarification is needed")
    suggested_options: Optional[List[str]] = Field(default=[], description="Quick multiple-choice options for the user")
    action_checklist: Optional[List[str]] = Field(default=[], description="Step-by-step resolution plan")
    recommended_services: Optional[List[MatchedService]] = Field(default=[], description="Verified real-world services")
