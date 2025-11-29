from datetime import datetime
from typing import Dict
from models.state import InterviewState
from services.llm_service import calculate_cv_score
from utils.logger import get_logger

logger = get_logger(__name__)


def closing_phase(state: InterviewState) -> InterviewState:
    """Nodo síncrono para cierre, compatible con interview_graph.invoke()."""
    try:
        logger.info(
            "closing_phase_started",
            application_id=state.get("application_id"),
        )

        # 1. CV score (solo local, sin backend async)
        cv_score_data = _calculate_cv_score_safe(state)
        state["cv_score"] = cv_score_data["score"]
        state["cv_score_explanation"] = cv_score_data["explanation"]

        # 2. Promedios
        technical_avg = _calculate_phase_average(state.get("technical_scores", []))
        state["technical_score_avg"] = technical_avg["score"]
        state["technical_score_explanation"] = technical_avg["explanation"]

        soft_skills_avg = _calculate_phase_average(state.get("soft_skills_scores", []))
        state["soft_skills_score_avg"] = soft_skills_avg["score"]
        state["soft_skills_score_explanation"] = soft_skills_avg["explanation"]

        # 3. Global score (fórmula local)
        global_score_data = _calculate_global_score_safe(
            state,
            cv_score_data["score"],
            technical_avg["score"],
            soft_skills_avg["score"],
        )
        state["global_score"] = global_score_data["global_score"]
        state["global_score_explanation"] = global_score_data["explanation"]

        # 4. Mensaje de cierre
        closing_message = _generate_closing_message(state)
        message_order = len(state.get("messages", []))
        state["messages"].append({
            "role": "agent",
            "content": closing_message,
            "timestamp": datetime.utcnow().isoformat(),
            "category": "closing",
            "order_index": message_order,
        })

        state["next_question"] = closing_message
        state["should_continue"] = False
        state["current_phase"] = "closing"

        logger.info(
            "interview_completed",
            application_id=state.get("application_id"),
            global_score=state["global_score"],
            cv_score=state["cv_score"],
            technical_score=state["technical_score_avg"],
            soft_skills_score=state["soft_skills_score_avg"],
        )
        return state

    except Exception as e:
        logger.error(
            "closing_phase_failed",
            application_id=state.get("application_id"),
            error=str(e),
        )
        raise


def _calculate_cv_score_safe(state: InterviewState) -> Dict:
    """Síncrono: usa solo LLM local para CV."""
    try:
        return calculate_cv_score(
            state["candidate_context"]["cv_text"],
            state["job_context"],
        )
    except Exception as e:
        logger.warning("backend_cv_score_failed_using_local", error=str(e))
        return {"score": 0.0, "explanation": "No se pudo calcular el CV score"}


def _calculate_phase_average(scores: list) -> Dict:
    if not scores:
        return {
            "score": 0.0,
            "explanation": "No se completaron preguntas en esta fase",
        }
    vals = [s["score"] for s in scores]
    avg = sum(vals) / len(vals)
    normalized = (avg / 5.0) * 100
    expls = [s.get("explanation", "") for s in scores if s.get("explanation")]
    combined = " | ".join(expls[:3])
    if len(combined) > 200:
        combined = combined[:197] + "..."
    return {
        "score": round(normalized, 1),
        "explanation": combined or f"Promedio de {len(scores)} respuestas evaluadas",
    }


def _calculate_global_score_safe(
    state: InterviewState,
    cv_score: float,
    technical_score: float,
    soft_skills_score: float,
) -> Dict:
    """Síncrono: cálculo ponderado local."""
    global_score = (cv_score * 0.4) + (technical_score * 0.4) + (soft_skills_score * 0.2)
    return {
        "global_score": round(global_score, 1),
        "explanation": (
            f"Score ponderado: CV {cv_score:.0f} (40%) + "
            f"Técnica {technical_score:.0f} (40%) + "
            f"Soft {soft_skills_score:.0f} (20%)"
        ),
    }

def _generate_closing_message(state: InterviewState) -> str:
    """Generate personalized closing message."""
    candidate_name = state["candidate_context"].get("name", "")
    global_score = state.get("global_score", 0)

    # Si hubo rechazo automático
    if state.get("rejection_reason"):
        return (
            f"Gracias por tu tiempo, {candidate_name}.\n\n"
            f"Hemos completado la evaluación inicial. En esta ocasión, no podremos continuar "
            f"con el proceso debido a: {state['rejection_reason']}\n\n"
            "Te deseamos éxito en tu búsqueda laboral."
        )

    # Cierre normal según score
    if global_score >= 75:
        tone = "Excelente desempeño"
    elif global_score >= 60:
        tone = "Buen desempeño"
    else:
        tone = "Evaluación completada"

    return (
        f"Gracias por completar la entrevista, {candidate_name}.\n\n"
        f"{tone} en el proceso. El equipo de reclutamiento revisará tus respuestas y "
        "te contactaremos pronto con los siguientes pasos.\n\n"
        "¡Que tengas un excelente día!"
    )
