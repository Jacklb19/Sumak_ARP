"""Evaluate knockout response node."""

from datetime import datetime
from models.state import InterviewState
from services.llm_service import evaluate_answer
from prompts.knockout_prompts import get_knockout_evaluation_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_knockout_response(state: InterviewState) -> InterviewState:
    """
    Evaluate candidate's knockout answer.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with evaluation
    """
    try:
        # Get last knockout question
        knockout_messages = [
            msg for msg in state.get("messages", [])
            if msg.get("category") == "knockout" and msg.get("role") == "agent"
        ]
        
        if not knockout_messages:
            logger.warning(
                "no_knockout_question_found",
                application_id=state.get("application_id")
            )
            return state
        
        last_question = knockout_messages[-1]["content"]
        candidate_answer = state.get("candidate_message", "")
        
        if not candidate_answer:
            logger.warning(
                "no_candidate_answer",
                application_id=state.get("application_id")
            )
            return state
        
        # Generate evaluation prompt
        prompt = get_knockout_evaluation_prompt(
            question=last_question,
            candidate_answer=candidate_answer,
            knockout_criteria=state["job_context"]["knockout_criteria"],
            job_title=state["job_context"]["title"]
        )
        
        # Evaluate answer
        evaluation = evaluate_answer(prompt)
        
        # Save candidate message
        message_order = len(state.get("messages", []))
        candidate_msg = {
            "role": "candidate",
            "content": candidate_answer,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "knockout",
            "order_index": message_order
        }
        state["messages"].append(candidate_msg)
        
        # Save score
        score_entry = {
            "question": last_question,
            "answer": candidate_answer,
            "score": evaluation.get("score", 3.0),
            "explanation": evaluation.get("explanation", ""),
            "auto_reject": evaluation.get("auto_reject", False)
        }
        state["knockout_scores"].append(score_entry)
        
        # Check for auto-rejection
        if evaluation.get("auto_reject", False):
            # Política: no auto-rechazar en la primera pregunta knockout
            if state["phase_counter"]["knockout"] <= 1:
                logger.info(
                    "knockout_auto_reject_ignored_first_question",
                    application_id=state.get("application_id"),
                    explanation=evaluation.get("explanation"),
                )
                state["current_phase"] = "knockout"
            else:
                logger.warning(
                    "candidate_auto_rejected",
                    application_id=state.get("application_id"),
                    reason=evaluation.get("explanation"),
                )
                state["should_continue"] = False
                state["current_phase"] = "closing"
                state["rejection_reason"] = f"Knockout: {evaluation.get('explanation')}"
            return state
        
        # Check if knockout phase is complete
        if state["phase_counter"]["knockout"] >= state["max_questions_per_phase"]["knockout"]:
            state["current_phase"] = "technical"
            state["completed_phases"].append("knockout")
            logger.info(
                "knockout_phase_completed",
                application_id=state.get("application_id"),
                total_questions=state["phase_counter"]["knockout"]
            )
        else:
            # More knockout questions needed
            state["current_phase"] = "knockout"
        
        logger.info(
            "knockout_answer_evaluated",
            application_id=state.get("application_id"),
            score=evaluation.get("score"),
            auto_reject=evaluation.get("auto_reject")
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "evaluate_knockout_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise
