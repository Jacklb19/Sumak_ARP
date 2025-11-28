from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class EvaluationStatus(str, Enum):
    """Evaluation status enum"""
    PENDING = "pending"
    CV_REVIEW = "cv_review"
    TECHNICAL_INTERVIEW = "technical_interview"
    BEHAVIORAL_INTERVIEW = "behavioral_interview"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentState(BaseModel):
    """
    Complete state object for the recruitment agent
    Flows through LangGraph nodes
    """
    
    # Identifiers
    candidate_id: str
    job_id: str
    company_id: str
    
    # Input data
    cv_text: str
    cv_url: Optional[str] = None
    job_requirements: List[str] = []
    job_description: str = ""
    
    # Process state
    status: EvaluationStatus = EvaluationStatus.PENDING
    current_step: str = "initialize"
    
    # Scores
    cv_score: Optional[float] = None
    technical_score: Optional[float] = None
    behavioral_score: Optional[float] = None
    overall_score: Optional[float] = None
    
    # Interview data
    questions_asked: List[str] = []
    answers_given: List[str] = []
    
    # Results
    recommendation: str = ""
    notes: str = ""
    errors: List[str] = []
    
    # Control flow
    should_continue_technical: bool = True
    should_continue_behavioral: bool = True
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
