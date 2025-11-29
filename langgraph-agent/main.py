"""FastAPI application for LangGraph Interview Agent."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any

from models.schemas import (
    InterviewStepRequest,
    InterviewStepResponse,
    ScoreSummary,
    HealthResponse,
    ErrorResponse
)
from models.state import InterviewState
from graph.interview_graph import interview_graph
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangGraph Interview Agent",
    description="AI-powered interview agent for candidate evaluation",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.environment,
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.environment,
        version="1.0.0"
    )


@app.post(
    "/interview-step",
    response_model=InterviewStepResponse,
    responses={
        500: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def interview_step(request: InterviewStepRequest) -> InterviewStepResponse:
    """
    Execute one step of the interview process.
    
    This endpoint is called by n8n workflow for each interaction.
    
    Flow:
    1. Receive application_id + candidate_message + interview_state
    2. Convert to InterviewState
    3. Execute graph (generates next question or evaluates answer)
    4. Return next_question + score + metadata
    
    Args:
        request: Interview step request with state
        
    Returns:
        Interview step response with next question
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(
            "interview_step_started",
            application_id=request.application_id,
            current_phase=request.interview_state.current_phase,
            has_message=bool(request.candidate_message)
        )
        
        # Build InterviewState from request
        state = _build_state_from_request(request)
        
        # Execute graph
        result = interview_graph.invoke(state)
        
        # Extract response data
        response = _build_response_from_state(result)
        
        logger.info(
            "interview_step_completed",
            application_id=request.application_id,
            phase=response.phase,
            score=response.score,
            should_continue=response.should_continue
        )
        
        return response
    
    except Exception as e:
        logger.error(
            "interview_step_failed",
            application_id=request.application_id,
            error=str(e),
            error_type=type(e).__name__
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview step processing failed: {str(e)}"
        )


def _build_state_from_request(request: InterviewStepRequest) -> InterviewState:
    """
    Build InterviewState from API request.
    
    Args:
        request: API request
        
    Returns:
        InterviewState dict
    """
    state_input = request.interview_state
    
    # Convert messages
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp,
            "category": msg.category,
            "order_index": msg.order_index
        }
        for msg in state_input.conversation_history
    ]
    
    state: InterviewState = {
        "application_id": request.application_id,
        "job_posting_id": state_input.job_posting_id,
        "candidate_id": state_input.candidate_id,
        "current_phase": state_input.current_phase,
        "completed_phases": state_input.completed_phases,
        "messages": messages,
        "candidate_message": request.candidate_message,
        "knockout_scores": state_input.knockout_scores,
        "technical_scores": state_input.technical_scores,
        "soft_skills_scores": state_input.soft_skills_scores,
        "should_continue": True,
        "next_question": ""
    }
    
    # Add phase_counter if provided
    if state_input.phase_counter:
        state["phase_counter"] = state_input.phase_counter
    
    return state


def _build_response_from_state(state: InterviewState) -> InterviewStepResponse:
    """
    Build API response from InterviewState.
    
    Args:
        state: Interview state after graph execution
        
    Returns:
        InterviewStepResponse
    """
    # Get last score
    all_scores = (
        state.get("knockout_scores", []) +
        state.get("technical_scores", []) +
        state.get("soft_skills_scores", [])
    )
    
    last_score = all_scores[-1]["score"] if all_scores else 0.0
    
    # Build scores summary
    scores_summary = ScoreSummary(
        knockout_completed=len(state.get("knockout_scores", [])),
        technical_completed=len(state.get("technical_scores", [])),
        soft_skills_completed=len(state.get("soft_skills_scores", [])),
        total_questions=len(all_scores)
    )
    
    # Get order index
    order_index = len(state.get("messages", []))
    
    return InterviewStepResponse(
        next_question=state.get("next_question", ""),
        score=last_score,
        phase=state.get("current_phase", "knockout"),
        should_continue=state.get("should_continue", True),
        scores_summary=scores_summary,
        rejection_reason=state.get("rejection_reason"),
        order_index=order_index
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__
    )
    
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.environment == "development" else "An error occurred"
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_server",
        host=settings.api_host,
        port=settings.api_port,
        environment=settings.environment
    )
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
