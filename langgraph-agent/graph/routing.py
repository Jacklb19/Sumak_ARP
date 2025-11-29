"""Routing logic for interview graph."""

from models.state import InterviewState
from utils.logger import get_logger

logger = get_logger(__name__)


def should_continue_interview(state: InterviewState) -> str:
    """
    Determine next route key based on current state.
    The returned value is a ROUTE KEY, not a node name.
    """
    if not state.get("should_continue", True):
        logger.info(
            "routing_to_closing_early",
            application_id=state.get("application_id"),
            reason=state.get("rejection_reason", "Interview completed"),
        )
        return "to_closing"

    current_phase = state.get("current_phase", "knockout")
    has_candidate_message = bool(state.get("candidate_message", "").strip())

    logger.debug(
        "routing_decision",
        application_id=state.get("application_id"),
        current_phase=current_phase,
        has_candidate_message=has_candidate_message,
    )

    result = None

    if current_phase == "knockout":
        if has_candidate_message:
            result = "to_eval_knockout"
        else:
            result = "stay_knockout"

    elif current_phase == "technical":
        if has_candidate_message:
            result = "to_eval_technical"
        else:
            result = "stay_technical"

    elif current_phase == "soft_skills":
        if has_candidate_message:
            result = "to_eval_soft_skills"
        else:
            result = "stay_soft_skills"

    elif current_phase == "closing":
        result = "to_closing"

    else:
        logger.warning(
            "unknown_phase_routing_to_closing",
            application_id=state.get("application_id"),
            phase=current_phase,
        )
        result = "to_closing"

    logger.debug(
        "routing_result",
        application_id=state.get("application_id"),
        next_route_key=result,
    )
    return result


def route_after_initialization(state: InterviewState) -> str:
    """Route after initialization node (always to knockout)."""
    return "to_knockout"


def route_after_evaluation(state: InterviewState) -> str:
    """Route after evaluation nodes."""
    return should_continue_interview(state)
