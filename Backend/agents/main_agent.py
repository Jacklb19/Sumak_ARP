
from langgraph.graph import StateGraph, END
from schemas.state import AgentState
from .cv_evaluator import evaluate_cv_node, should_continue_to_interview
from .interviewer import ask_technical_question_node, ask_behavioral_question_node
from .scorer import score_candidate_node

def create_recruitment_agent():
    """
    Creates and returns the compiled LangGraph recruitment evaluation agent
    
    Flow:
    1. evaluate_cv → cv_score, should_continue decision
    2. (if should_continue) → ask_technical_question → ask_behavioral_question
    3. score_candidate → final scores and recommendation
    """
    
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("evaluate_cv", evaluate_cv_node)
    graph.add_node("technical_questions", ask_technical_question_node)
    graph.add_node("behavioral_questions", ask_behavioral_question_node)
    graph.add_node("score", score_candidate_node)
    
    # Set entry point
    graph.set_entry_point("evaluate_cv")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "evaluate_cv",
        should_continue_to_interview,
        {
            True: "technical_questions",
            False: "score"
        }
    )
    
    # Add regular edges
    graph.add_edge("technical_questions", "behavioral_questions")
    graph.add_edge("behavioral_questions", "score")
    graph.add_edge("score", END)
    
    # Compile and return
    return graph.compile()
