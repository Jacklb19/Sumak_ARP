"""Knockout phase node - Generate knockout questions."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import generate_question
from prompts.knockout_prompts import get_knockout_question_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def knockout_phase(state: InterviewState) -> InterviewState:
    """
    Generate knockout question.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with new knockout question
    """
    try:
        # Check if knockout phase is complete
        if state["phase_counter"]["knockout"] >= state["max_questions_per_phase"]["knockout"]:
            logger.info(
                "knockout_phase_complete",
                application_id=state.get("application_id"),
                questions_asked=state["phase_counter"]["knockout"]
            )
            state["current_phase"] = "technical"
            state["completed_phases"].append("knockout")
            return state
        
        # Extract previous questions
        previous_questions = [
            score["question"] 
            for score in state.get("knockout_scores", [])
        ]
        
        # Generate prompt
        prompt = get_knockout_question_prompt(
            job_title=state["job_context"]["title"],
            knockout_criteria=state["job_context"]["knockout_criteria"],
            cv_text=state["candidate_context"]["cv_text"],
            previous_questions=previous_questions
        )
        
        # Generate question
        question = generate_question(prompt)
        
        # Create message
        message_order = len(state.get("messages", []))
        message = {
            "role": "agent",
            "content": question,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "knockout",
            "order_index": message_order
        }
        
        # Update state
        state["messages"].append(message)
        state["next_question"] = question
        state["phase_counter"]["knockout"] += 1
        
        logger.info(
            "knockout_question_generated",
            application_id=state.get("application_id"),
            question_number=state["phase_counter"]["knockout"],
            question_preview=question[:50]
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "knockout_phase_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
