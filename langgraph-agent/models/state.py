"""Interview state definition for LangGraph."""

from typing import TypedDict, List, Dict, Annotated, Optional
import operator


class InterviewState(TypedDict, total=False):
    """
    Complete state for interview graph.
    
    Uses total=False to allow gradual state building across nodes.
    """

    # === Identifiers ===
    application_id: str
    job_posting_id: str
    candidate_id: str

    # === Context (loaded in initialize) ===
    job_context: Dict[str, any]
    """
    Structure:
    {
        "title": str,
        "description": str,
        "required_skills": dict,
        "nice_to_have_skills": dict,
        "knockout_criteria": dict,
        "custom_questions": list[str]
    }
    """

    candidate_context: Dict[str, any]
    """
    Structure:
    {
        "name": str,
        "email": str,
        "cv_text": str,
        "seniority": str,
        "expected_salary": int
    }
    """

    # === Interview State ===
    current_phase: str  # 'knockout', 'technical', 'soft_skills', 'closing'
    completed_phases: List[str]

    # === Messages (accumulate with operator.add) ===
    messages: Annotated[List[Dict[str, any]], operator.add]
    """
    Structure of each message:
    {
        "role": "agent" | "candidate",
        "content": str,
        "timestamp": str (ISO format),
        "category": "knockout" | "technical" | "soft_skills" | "closing",
        "order_index": int
    }
    """

    candidate_message: str  # Last message from candidate

    # === Scores per Phase ===
    knockout_scores: List[Dict[str, any]]
    """
    Structure:
    {
        "question": str,
        "answer": str,
        "score": float (1-5),
        "explanation": str,
        "auto_reject": bool
    }
    """

    technical_scores: List[Dict[str, any]]
    """
    Structure:
    {
        "question": str,
        "answer": str,
        "score": float (1-5),
        "explanation": str,
        "difficulty": "easy" | "medium" | "hard"
    }
    """

    soft_skills_scores: List[Dict[str, any]]
    """
    Structure:
    {
        "question": str,
        "answer": str,
        "score": float (1-5),
        "explanation": str,
        "competency": str
    }
    """

    # === Question Counters ===
    phase_counter: Dict[str, int]
    """Current count per phase: {"knockout": 2, "technical": 3, ...}"""

    max_questions_per_phase: Dict[str, int]
    """Max questions allowed: {"knockout": 3, "technical": 5, ...}"""

    # === Control Flow ===
    should_continue: bool
    next_question: str
    rejection_reason: Optional[str]

    # === Final Scores (calculated in closing) ===
    cv_score: Optional[float]
    cv_score_explanation: Optional[str]
    technical_score_avg: Optional[float]
    technical_score_explanation: Optional[str]
    soft_skills_score_avg: Optional[float]
    soft_skills_score_explanation: Optional[str]
    global_score: Optional[float]
    global_score_explanation: Optional[str]
