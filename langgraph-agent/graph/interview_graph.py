"""LangGraph interview graph construction."""

from langgraph.graph import StateGraph, END
from models.state import InterviewState
from nodes import (
    initialize_interview,
    knockout_phase,
    evaluate_knockout_response,
    technical_phase,
    evaluate_technical_response,
    soft_skills_phase,
    evaluate_soft_skills_response,
    closing_phase,
)
from graph.routing import (
    should_continue_interview,
    route_after_initialization,
    route_after_evaluation,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def create_interview_graph() -> StateGraph:
    """
    Create and compile the interview graph.
    """
    graph = StateGraph(InterviewState)

    # Nodes
    graph.add_node("initialize", initialize_interview)
    graph.add_node("knockout", knockout_phase)
    graph.add_node("evaluate_knockout", evaluate_knockout_response)
    graph.add_node("technical", technical_phase)
    graph.add_node("evaluate_technical", evaluate_technical_response)
    graph.add_node("soft_skills", soft_skills_phase)
    graph.add_node("evaluate_soft_skills", evaluate_soft_skills_response)
    graph.add_node("closing", closing_phase)

    # Entry
    graph.set_entry_point("initialize")

    # After initialization
    graph.add_conditional_edges(
        "initialize",
        route_after_initialization,
        {
            "to_knockout": "knockout",
        },
    )

    # Knockout phase
    graph.add_conditional_edges(
        "knockout",
        should_continue_interview,
        {
            "stay_knockout": "knockout",
            "to_eval_knockout": "evaluate_knockout",
            "to_closing": "closing",
        },
    )

    graph.add_conditional_edges(
        "evaluate_knockout",
        should_continue_interview,
        {
            "stay_knockout": "knockout",
            "to_eval_knockout": "evaluate_knockout",
            "to_closing": "closing",
            "stay_technical": "technical",
            "to_eval_technical": "evaluate_technical",
        },
    )

    # Technical phase
    graph.add_conditional_edges(
        "technical",
        should_continue_interview,
        {
            "stay_technical": "technical",
            "to_eval_technical": "evaluate_technical",
            "to_closing": "closing",
        },
    )

    graph.add_conditional_edges(
        "evaluate_technical",
        should_continue_interview,
        {
            "stay_technical": "technical",
            "stay_soft_skills": "soft_skills",
            "to_eval_soft_skills": "evaluate_soft_skills",
            "to_closing": "closing",
        },
    )

    # Soft skills phase
    graph.add_conditional_edges(
        "soft_skills",
        should_continue_interview,
        {
            "stay_soft_skills": "soft_skills",
            "to_eval_soft_skills": "evaluate_soft_skills",
            "to_closing": "closing",
        },
    )

    graph.add_conditional_edges(
        "evaluate_soft_skills",
        should_continue_interview,
        {
            "stay_soft_skills": "soft_skills",
            "to_closing": "closing",
        },
    )

    # Closing → END
    graph.add_edge("closing", END)

    logger.info("interview_graph_created")
    return graph


interview_graph = create_interview_graph().compile()
logger.info("interview_graph_compiled")
