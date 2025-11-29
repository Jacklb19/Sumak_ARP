"""Closing node - Calculate final scores and generate closing message."""

from datetime import datetime
from typing import Dict
from models.state import InterviewState
from services.llm_service import calculate_cv_score
from services.backend_client import call_backend_cv_score, call_backend_global_score
from utils.logger import get_logger

logger = get_logger(__name__)


def closing_phase(state: InterviewState) -> InterviewState:
    """
    Calculate final scores and generate closing message.
    
    Args:
        state: Current interview state
        
    Returns:
        Updated state with final scores
    """
    try:
        logger.info(
            "closing_phase_started",
            application_id=state.get("application_id")
        )
        
        # Calculate CV score (call backend or local LLM)
        cv_score_data = _calculate_cv_score_safe(state)
        state["cv_score"] = cv_score_data["score"]
        state["cv_score_explanation"] = cv_score_data["explanation"]
        
        # Calculate technical score average
        technical_avg = _calculate_phase_average(state.get("technical_scores", []))
        state["technical_score_avg"] = technical_avg["score"]
        state["technical_score_explanation"] = technical_avg["explanation"]
        
        # Calculate soft skills score average
        soft_skills_avg = _calculate_phase_average(state.get("soft_skills_scores", []))
        state["soft_skills_score_avg"] = soft_skills_avg["score"]
        state["soft_skills_score_explanation"] = soft_skills_avg["explanation"]
        
        # Calculate global score (call backend or local calculation)
        global_score_data = _calculate_global_score_safe(
            state,
            cv_score_data["score"],
            technical_avg["score"],
            soft_skills_avg["score"]
        )
        state["global_score"] = global_score_data["global_score"]
        state["global_score_explanation"] = global_score_data["explanation"]
        
        # Generate closing message
        closing_message = _generate_closing_message(state)
        
        message_order = len(state.get("messages", []))
        message = {
            "role": "agent",
            "content": closing_message,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "closing",
            "order_index": message_order
        }
        
        state["messages"].append(message)
        state["next_question"] = closing_message
        state["should_continue"] = False
        state["current_phase"] = "completed"
        
        logger.info(
            "interview_completed",
            application_id=state.get("application_id"),
            global_score=state["global_score"],
            cv_score=state["cv_score"],
            technical_score=state["technical_score_avg"],
            soft_skills_score=state["soft_skills_score_avg"]
        )
        
        return state
    
    except Exception as e:
        logger.error(
            "closing_phase_failed",
            application_id=state.get("application_id"),
            error=str(e)
        )
        raise


def _calculate_cv_score_safe(state: InterviewState) -> Dict:
    """
    Calculate CV score with fallback.
    
    Tries backend first, falls back to local LLM.
    """
    try:
        # Try backend API (async wrapper needed in production)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            call_backend_cv_score(
                state["candidate_id"],
                state["job_posting_id"]
            )
        )
        loop.close()
        
        return result
    
    except Exception as e:
        logger.warning(
            "backend_cv_score_failed_using_local",
            error=str(e)
        )
        
        # Fallback to local LLM
        return calculate_cv_score(
            state["candidate_context"]["cv_text"],
            state["job_context"]
        )


def _calculate_phase_average(scores: list) -> Dict:
    """Calculate average score for a phase."""
    if not scores:
        return {
            "score": 0.0,
            "explanation": "No se completaron preguntas en esta fase"
        }
    
    # Convert 1-5 scale to 0-100 scale
    score_values = [s["score"] for s in scores]
    avg_score = sum(score_values) / len(score_values)
    normalized_score = (avg_score / 5.0) * 100  # Convert to 0-100
    
    # Generate explanation
    explanations = [s.get("explanation", "") for s in scores if s.get("explanation")]
    combined_explanation = " | ".join(explanations[:3])  # Take first 3
    
    if len(combined_explanation) > 200:
        combined_explanation = combined_explanation[:197] + "..."
    
    return {
        "score": round(normalized_score, 1),
        "explanation": combined_explanation or f"Promedio de {len(scores)} respuestas evaluadas"
    }


def _calculate_global_score_safe(
    state: InterviewState,
    cv_score: float,
    technical_score: float,
    soft_skills_score: float
) -> Dict:
    """
    Calculate global score with fallback.
    
    Tries backend first, falls back to local calculation.
    """
    try:
        # Try backend API
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            call_backend_global_score(
                state["application_id"],
                cv_score,
                technical_score,
                soft_skills_score
            )
        )
        loop.close()
        
        return result
    
    except Exception as e:
        logger.warning(
            "backend_global_score_failed_using_local",
            error=str(e)
        )
        
        # Fallback to local calculation: 40% CV + 40% technical + 20% soft
        global_score = (cv_score * 0.4) + (technical_score * 0.4) + (soft_skills_score * 0.2)
        
        return {
            "global_score": round(global_score, 1),
            "explanation": f"Score ponderado: CV {cv_score:.0f} (40%) + Técnica {technical_score:.0f} (40%) + Soft {soft_skills_score:.0f} (20%)"
        }


def _generate_closing_message(state: InterviewState) -> str:
    """Generate personalized closing message."""
    
    candidate_name = state["candidate_context"].get("name", "")
    global_score = state.get("global_score", 0)
    
    # Check if rejected
    if state.get("rejection_reason"):
        return f"""Gracias por tu tiempo, {candidate_name}. 

Hemos completado la evaluación inicial. En esta ocasión, no podremos continuar con el proceso debido a: {state["rejection_reason"]}

Te deseamos éxito en tu búsqueda laboral."""
    
    # Successful completion
    if global_score >= 75:
        tone = "Excelente desempeño"
    elif global_score >= 60:
        tone = "Buen desempeño"
    else:
        tone = "Evaluación completada"
    
    return f"""Gracias por completar la entrevista, {candidate_name}. 

{tone} en el proceso. El equipo de reclutamiento revisará tus respuestas y te contactaremos pronto con los siguientes pasos.

¡Que tengas un excelente día!"""
