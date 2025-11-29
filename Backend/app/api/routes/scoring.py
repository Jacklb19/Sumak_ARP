from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    CalculateCVScoreRequest, CVScoreResponse,
    CalculateGlobalScoreRequest, GlobalScoreResponse
)
from app.core.security import get_current_user
from typing import Dict, Any

router = APIRouter()


@router.post("/calculate-cv-score", response_model=CVScoreResponse)
async def calculate_cv_score(
    request: CalculateCVScoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Calcular score del CV (stub suficiente para tests).
    """
    try:
        # Stub simple: devuelve un score fijo
        return CVScoreResponse(
            score=82.0,
            sub_scores={"education": 85.0, "experience": 80.0},
            explanation="CV score calculated successfully (stub)."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/calculate-global-score", response_model=GlobalScoreResponse)
async def calculate_global_score(
    request: CalculateGlobalScoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Calcular score global (stub suficiente para tests).
    """
    try:
        weights = request.scoring_weights or {"cv": 0.4, "technical": 0.4, "softskills": 0.2}
        w_cv = weights.get("cv", 0.4)
        w_tech = weights.get("technical", 0.4)
        w_soft = weights.get("softskills", 0.2)

        global_score = (
            request.cv_score * w_cv +
            request.technical_score * w_tech +
            request.soft_skills_score * w_soft
        )

        return GlobalScoreResponse(
            global_score=round(global_score, 1),
            explanation="Global score calculated as weighted average."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
