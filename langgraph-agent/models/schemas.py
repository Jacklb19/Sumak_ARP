"""Pydantic schemas for API requests and responses."""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class MessageDict(BaseModel):
    """Message structure in conversation history."""
    role: str = Field(..., pattern="^(agent|candidate)$")
    content: str = Field(..., min_length=1)
    timestamp: str
    category: Optional[str] = Field(
        None,
        pattern="^(knockout|technical|soft_skills|closing)$"
    )
    order_index: Optional[int] = Field(None, ge=0)


class JobContext(BaseModel):
    """Job metadata needed by the graph."""
    title: str
    knockout_criteria: List[str] = Field(default_factory=list)


class MaxQuestionsPerPhase(BaseModel):
    """Max questions per interview phase."""
    knockout: int = 1
    technical: int = 3
    soft_skills: int = 2


class InterviewStateInput(BaseModel):
    """Interview state received from n8n."""
    job_posting_id: str = Field(..., description="UUID of job posting")
    candidate_id: str = Field(..., description="UUID of candidate")
    current_phase: str = Field(
        default="knockout",
        pattern="^(knockout|technical|soft_skills|closing)$"
    )
    completed_phases: List[str] = Field(default_factory=list)
    conversation_history: List[MessageDict] = Field(default_factory=list)
    phase_counter: Optional[Dict[str, int]] = None
    knockout_scores: List[Dict] = Field(default_factory=list)
    technical_scores: List[Dict] = Field(default_factory=list)
    soft_skills_scores: List[Dict] = Field(default_factory=list)

    # 🔹 Campos nuevos requeridos por los nodos
    job_context: JobContext
    max_questions_per_phase: MaxQuestionsPerPhase
    rejection_reason: Optional[str] = None


class InterviewStepRequest(BaseModel):
    """Request body for /interview-step endpoint."""
    application_id: str = Field(..., description="UUID of application")
    candidate_message: str = Field(
        default="",
        description="Last message from candidate (empty on first call)"
    )
    interview_state: InterviewStateInput

    @field_validator("application_id", "interview_state")
    @classmethod
    def validate_not_empty(cls, v):
        """Ensure required fields are not empty."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class ScoreSummary(BaseModel):
    """Summary of scores per phase."""
    knockout_completed: int = Field(ge=0)
    technical_completed: int = Field(ge=0)
    soft_skills_completed: int = Field(ge=0)
    total_questions: int = Field(ge=0)


class InterviewStepResponse(BaseModel):
    """Response from /interview-step endpoint."""
    next_question: str = Field(..., description="Question to send to candidate")
    score: float = Field(..., ge=0, le=5, description="Score of last answer (0 if first)")
    phase: str = Field(..., pattern="^(knockout|technical|soft_skills|closing)$")
    should_continue: bool = Field(..., description="Whether to continue interview")
    scores_summary: ScoreSummary
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")
    order_index: int = Field(..., ge=0, description="Message order in conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "next_question": "¿Cuántos años de experiencia tienes con Python?",
                "score": 4.5,
                "phase": "technical",
                "should_continue": True,
                "scores_summary": {
                    "knockout_completed": 3,
                    "technical_completed": 2,
                    "soft_skills_completed": 0,
                    "total_questions": 5
                },
                "rejection_reason": None,
                "order_index": 6
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    environment: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
