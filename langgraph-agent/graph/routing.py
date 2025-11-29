"""Routing logic for interview graph."""

from models.state import InterviewState
from utils.logger import get_logger

logger = get_logger(__name__)


def should_continue_interview(state: InterviewState) -> str:
    """
    Determine next node based on current state.
    
    This is the core routing logic for the interview graph.
    
    Args:
        state: Current interview state
        
    Returns:
        Name of next node to execute
    """
    # Check if interview should end
    if not state.get("should_continue", True):
        logger.info(
            "routing_to_closing_early",
            application_id=state.get("application_id"),
            reason=state.get("rejection_reason", "Interview completed")
        )
        return "closing"
    
    current_phase = state.get("current_phase", "knockout")
    has_candidate_message = bool(state.get("candidate_message", "").strip())
    
    logger.debug(
        "routing_decision",
        application_id=state.get("application_id"),
        current_phase=current_phase,
        has_candidate_message=has_candidate_message
    )
    
    # Routing logic per phase
    if current_phase == "knockout":
        if has_candidate_message:
            return "evaluate_knockout"
        else:
            return "knockout"
    
    elif current_phase == "technical":
        if has_candidate_message:
            return "evaluate_technical"
        else:
            return "technical"
    
    elif current_phase == "soft_skills":
        if has_candidate_message:
            return "evaluate_soft_skills"
        else:
            return "soft_skills"
    
    elif current_phase == "closing":
        return "closing"
    
    else:
        # Fallback: should not happen
        logger.warning(
            "unknown_phase_routing_to_closing",
            application_id=state.get("application_id"),
            phase=current_phase
        )
        return "closing"


def route_after_initialization(state: InterviewState) -> str:
    """
    Route after initialization node.
    
    Args:
        state: Current interview state
        
    Returns:
        Name of next node (always 'knockout')
    """
    return "knockout"


def route_after_evaluation(state: InterviewState) -> str:
    """
    Route after evaluation nodes.
    
    Determines whether to continue in same phase, move to next phase, or close.
    
    Args:
        state: Current interview state
        
    Returns:
        Name of next node
    """
    return should_continue_interview(state)
