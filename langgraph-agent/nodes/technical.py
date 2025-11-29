"""Technical phase node - Generate adaptive technical questions."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import generate_question
from prompts.technical_prompts import get_technical_question_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def technical_phase(state: InterviewState) -> InterviewState:
    """
    Generate adaptive technical question.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with new technical question
    """
    try:
        # Check if technical phase is complete
        if state["phase_counter"]["technical"] >= state["max_questions_per_phase"]["technical"]:
            logger.info(
                "technical_phase_complete",
                application_id=state.get("application_id"),
                questions_asked=state["phase_counter"]["technical"]
            )
            state["current_phase"] = "soft_skills"
            state["completed_phases"].append("technical")
            return state
        
        # Extract previous questions and scores
        previous_questions = [
            score["question"]
            for score in state.get("technical_scores", [])
        ]
        
        previous_scores = state.get("technical_scores", [])
        
        # Generate prompt
        prompt = get_technical_question_prompt(
            job_title=state["job_context"]["title"],
            required_skills=state["job_context"]["required_skills"],
            cv_text=state["candidate_context"]["cv_text"],
            seniority=state["candidate_context"]["seniority"],
            previous_questions=previous_questions,
            previous_scores=previous_scores
        )
        
        # Generate question
        question = generate_question(prompt)
        
        # Create message
        message_order = len(state.get("messages", []))
        message = {
            "role": "agent",
            "content": question,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "technical",
            "order_index": message_order
        }
        
        # Update state
        state["messages"].append(message)
        state["next_question"] = question
        state["phase_counter"]["technical"] += 1
        
        logger.info(
            "technical_question_generated",
            application_id=state.get("application_id"),
            question_number=state["phase_counter"]["technical"],
            question_preview=question[:50]
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "technical_phase_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
