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
    closing_phase
)
from graph.routing import (
    should_continue_interview,
    route_after_initialization,
    route_after_evaluation
)
from utils.logger import get_logger

logger = get_logger(__name__)


def create_interview_graph() -> StateGraph:
    """
    Create and compile the interview graph.
    
    Graph structure:
    
    initialize
        ↓
    knockout ⟷ evaluate_knockout
        ↓
    technical ⟷ evaluate_technical
        ↓
    soft_skills ⟷ evaluate_soft_skills
        ↓
    closing → END
    
    Returns:
        Compiled StateGraph
    """
    
    # Create graph
    graph = StateGraph(InterviewState)
    
    # Add nodes
    graph.add_node("initialize", initialize_interview)
    graph.add_node("knockout", knockout_phase)
    graph.add_node("evaluate_knockout", evaluate_knockout_response)
    graph.add_node("technical", technical_phase)
    graph.add_node("evaluate_technical", evaluate_technical_response)
    graph.add_node("soft_skills", soft_skills_phase)
    graph.add_node("evaluate_soft_skills", evaluate_soft_skills_response)
    graph.add_node("closing", closing_phase)
    
    # Set entry point
    graph.set_entry_point("initialize")
    
    # Add edges
    
    # After initialization, always go to knockout
    graph.add_conditional_edges(
        "initialize",
        route_after_initialization,
        {
            "knockout": "knockout"
        }
    )
    
    # Knockout phase routing
    graph.add_conditional_edges(
        "knockout",
        should_continue_interview,
        {
            "knockout": "knockout",
            "evaluate_knockout": "evaluate_knockout",
            "closing": "closing"
        }
    )
    
    graph.add_conditional_edges(
        "evaluate_knockout",
        should_continue_interview,
        {
            "knockout": "knockout",
            "technical": "technical",
            "closing": "closing"
        }
    )
    
    # Technical phase routing
    graph.add_conditional_edges(
        "technical",
        should_continue_interview,
        {
            "technical": "technical",
            "evaluate_technical": "evaluate_technical",
            "closing": "closing"
        }
    )
    
    graph.add_conditional_edges(
        "evaluate_technical",
        should_continue_interview,
        {
            "technical": "technical",
            "soft_skills": "soft_skills",
            "closing": "closing"
        }
    )
    
    # Soft skills phase routing
    graph.add_conditional_edges(
        "soft_skills",
        should_continue_interview,
        {
            "soft_skills": "soft_skills",
            "evaluate_soft_skills": "evaluate_soft_skills",
            "closing": "closing"
        }
    )
    
    graph.add_conditional_edges(
        "evaluate_soft_skills",
        should_continue_interview,
        {
            "soft_skills": "soft_skills",
            "closing": "closing"
        }
    )
    
    # Closing always ends
    graph.add_edge("closing", END)
    
    logger.info("interview_graph_created")
    
    return graph


# Create singleton instance
interview_graph = create_interview_graph().compile()

logger.info("interview_graph_compiled")
