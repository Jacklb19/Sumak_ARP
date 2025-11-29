"""Soft skills phase node - Generate behavioral questions."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import generate_question
from prompts.soft_skills_prompts import get_soft_skills_question_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def soft_skills_phase(state: InterviewState) -> InterviewState:
    """
    Generate soft skills behavioral question.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with new soft skills question
    """
    try:
        # Check if soft skills phase is complete
        if state["phase_counter"]["soft_skills"] >= state["max_questions_per_phase"]["soft_skills"]:
            logger.info(
                "soft_skills_phase_complete",
                application_id=state.get("application_id"),
                questions_asked=state["phase_counter"]["soft_skills"]
            )
            state["current_phase"] = "closing"
            state["completed_phases"].append("soft_skills")
            return state
        
        # Extract previous questions
        previous_questions = [
            score["question"]
            for score in state.get("soft_skills_scores", [])
        ]
        
        # Generate prompt
        prompt = get_soft_skills_question_prompt(
            job_title=state["job_context"]["title"],
            job_description=state["job_context"]["description"],
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
            "category": "soft_skills",
            "order_index": message_order
        }
        
        # Update state
        state["messages"].append(message)
        state["next_question"] = question
        state["phase_counter"]["soft_skills"] += 1
        
        logger.info(
            "soft_skills_question_generated",
            application_id=state.get("application_id"),
            question_number=state["phase_counter"]["soft_skills"],
            question_preview=question[:50]
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "soft_skills_phase_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
