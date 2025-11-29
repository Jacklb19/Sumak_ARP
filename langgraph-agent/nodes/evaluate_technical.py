"""Evaluate technical response node."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import evaluate_answer
from prompts.technical_prompts import get_technical_evaluation_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_technical_response(state: InterviewState) -> InterviewState:
    """
    Evaluate candidate's technical answer.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with evaluation
    """
    try:
        # Get last technical question
        technical_messages = [
            msg for msg in state.get("messages", [])
            if msg.get("category") == "technical" and msg.get("role") == "agent"
        ]
        
        if not technical_messages:
            logger.warning(
                "no_technical_question_found",
                application_id=state.get("application_id")
            )
            return state
        
        last_question = technical_messages[-1]["content"]
        candidate_answer = state.get("candidate_message", "")
        
        if not candidate_answer:
            logger.warning(
                "no_candidate_answer",
                application_id=state.get("application_id")
            )
            return state
        
        # Generate evaluation prompt
        prompt = get_technical_evaluation_prompt(
            question=last_question,
            candidate_answer=candidate_answer,
            expected_keywords=[],  # LLM will infer
            required_skills=state["job_context"]["required_skills"],
            seniority=state["candidate_context"]["seniority"]
        )
        
        # Evaluate answer
        evaluation = evaluate_answer(prompt)
        
        # Save candidate message
        message_order = len(state.get("messages", []))
        candidate_msg = {
            "role": "candidate",
            "content": candidate_answer,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "technical",
            "order_index": message_order
        }
        state["messages"].append(candidate_msg)
        
        # Save score
        score_entry = {
            "question": last_question,
            "answer": candidate_answer,
            "score": evaluation.get("score", 3.0),
            "explanation": evaluation.get("explanation", ""),
            "difficulty": evaluation.get("difficulty", "medium")
        }
        state["technical_scores"].append(score_entry)
        
        # Check if technical phase is complete
        if state["phase_counter"]["technical"] >= state["max_questions_per_phase"]["technical"]:
            state["current_phase"] = "soft_skills"
            state["completed_phases"].append("technical")
            logger.info(
                "technical_phase_completed",
                application_id=state.get("application_id"),
                total_questions=state["phase_counter"]["technical"]
            )
        else:
            # More technical questions needed
            state["current_phase"] = "technical"
        
        logger.info(
            "technical_answer_evaluated",
            application_id=state.get("application_id"),
            score=evaluation.get("score"),
            difficulty=evaluation.get("difficulty")
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "evaluate_technical_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
