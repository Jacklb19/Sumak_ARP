"""Initialize node - Load context and setup interview state."""

from models.state import InterviewState
from services.supabase_client import get_job_posting, get_candidate
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def initialize_interview(state: InterviewState) -> InterviewState:
    """
    Initialize interview by loading job and candidate context.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with context loaded
    """
    try:
        logger.info(
            "initializing_interview",
            application_id=state.get("application_id"),
            job_id=state.get("job_posting_id"),
            candidate_id=state.get("candidate_id")
        )
        
        # Fetch job posting
        job_data = get_job_posting(state["job_posting_id"])
        
        # Fetch candidate
        candidate_data = get_candidate(state["candidate_id"])
        
        # Build job context
        state["job_context"] = {
            "title": job_data.get("title", ""),
            "description": job_data.get("description", ""),
            "required_skills": job_data.get("required_skills", {}),
            "nice_to_have_skills": job_data.get("nice_to_have_skills", {}),
            "knockout_criteria": job_data.get("knockout_criteria", {}),
            "custom_questions": job_data.get("custom_questions", [])
        }
        
        # Build candidate context
        cv_text = candidate_data.get("cv_text_extracted", "")
        state["candidate_context"] = {
            "name": candidate_data.get("full_name", "Candidato"),
            "email": candidate_data.get("email", ""),
            "cv_text": cv_text[:settings.cv_context_length],  # Limit context
            "seniority": candidate_data.get("seniority_level", "mid"),
            "expected_salary": candidate_data.get("expected_salary")
        }
        
        # Initialize interview state
        state["current_phase"] = "knockout"
        state["completed_phases"] = []
        
        # Initialize score lists
        state["knockout_scores"] = []
        state["technical_scores"] = []
        state["soft_skills_scores"] = []
        
        # Initialize counters
        state["phase_counter"] = {
            "knockout": 0,
            "technical": 0,
            "soft_skills": 0
        }
        
        state["max_questions_per_phase"] = {
            "knockout": settings.max_knockout_questions,
            "technical": settings.max_technical_questions,
            "soft_skills": settings.max_soft_skills_questions
        }
        
        # Initialize control flags
        state["should_continue"] = True
        state["next_question"] = ""
        state["rejection_reason"] = None
        
        # Initialize messages if not present
        if "messages" not in state:
            state["messages"] = []
        
        logger.info(
            "interview_initialized",
            application_id=state.get("application_id"),
            job_title=state["job_context"]["title"],
            candidate_name=state["candidate_context"]["name"]
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "initialize_interview_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
