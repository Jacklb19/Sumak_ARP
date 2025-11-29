from fastapi import APIRouter as ScoringRouter, HTTPException, status, Depends
from app.models.schemas import (
    CalculateCVScoreRequest, CVScoreResponse,
    CalculateGlobalScoreRequest, GlobalScoreResponse
)
from app.services.scoring_service import ScoringService
from typing import Dict, Any

scoring_router = ScoringRouter()
scoring_service = ScoringService()


@scoring_router.post("/calculate-cv-score", response_model=CVScoreResponse)
async def calculate_cv_score(
    request: CalculateCVScoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Calcular score del CV (PARTE 3.2 - POST /scoring/calculate-cv-score)
    """
    try:
        result = await scoring_service.calculate_cv_score(
            request.candidate_id,
            request.job_posting_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@scoring_router.post("/calculate-global-score", response_model=GlobalScoreResponse)
async def calculate_global_score(
    request: CalculateGlobalScoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Calcular score global (PARTE 3.2 - POST /scoring/calculate-global-score)
    """
    try:
        result = await scoring_service.calculate_global_score(
            request.application_id,
            request.job_posting_id,
            request.cv_score,
            request.technical_score,
            request.soft_skills_score,
            request.scoring_weights
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )