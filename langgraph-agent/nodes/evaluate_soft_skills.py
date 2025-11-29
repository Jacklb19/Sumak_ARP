"""Evaluate soft skills response node."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import evaluate_answer
from prompts.soft_skills_prompts import get_soft_skills_evaluation_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_soft_skills_response(state: InterviewState) -> InterviewState:
    """
    Evaluate candidate's soft skills answer.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with evaluation
    """
    try:
        # Get last soft skills question
        soft_skills_messages = [
            msg for msg in state.get("messages", [])
            if msg.get("category") == "soft_skills" and msg.get("role") == "agent"
        ]
        
        if not soft_skills_messages:
            logger.warning(
                "no_soft_skills_question_found",
                application_id=state.get("application_id")
            )
            return state
        
        last_question = soft_skills_messages[-1]["content"]
        candidate_answer = state.get("candidate_message", "")
        
        if not candidate_answer:
            logger.warning(
                "no_candidate_answer",
                application_id=state.get("application_id")
            )
            return state
        
        # Extract competency from question context (simplified)
        competency = "Competencia conductual"  # LLM will infer specific one
        red_flags = ["Culpar a otros", "Falta de responsabilidad"]
        
        # Generate evaluation prompt
        prompt = get_soft_skills_evaluation_prompt(
            question=last_question,
            candidate_answer=candidate_answer,
            competency=competency,
            red_flags=red_flags
        )
        
        # Evaluate answer
        evaluation = evaluate_answer(prompt)
        
        # Save candidate message
        message_order = len(state.get("messages", []))
        candidate_msg = {
            "role": "candidate",
            "content": candidate_answer,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "soft_skills",
            "order_index": message_order
        }
        state["messages"].append(candidate_msg)
        
        # Save score
        score_entry = {
            "question": last_question,
            "answer": candidate_answer,
            "score": evaluation.get("score", 3.0),
            "explanation": evaluation.get("explanation", ""),
            "competency": evaluation.get("competency", competency)
        }
        state["soft_skills_scores"].append(score_entry)
        
        # Check if soft skills phase is complete
        if state["phase_counter"]["soft_skills"] >= state["max_questions_per_phase"]["soft_skills"]:
            state["current_phase"] = "closing"
            state["completed_phases"].append("soft_skills")
            logger.info(
                "soft_skills_phase_completed",
                application_id=state.get("application_id"),
                total_questions=state["phase_counter"]["soft_skills"]
            )
        else:
            # More soft skills questions needed
            state["current_phase"] = "soft_skills"
        
        logger.info(
            "soft_skills_answer_evaluated",
            application_id=state.get("application_id"),
            score=evaluation.get("score"),
            competency=evaluation.get("competency")
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "evaluate_soft_skills_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
