"""HTTP client for Backend API calls."""

import httpx
from typing import Dict, Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def call_backend_cv_score(candidate_id: str, job_posting_id: str) -> Dict:
    """
    Call backend to calculate CV score.
    
    Args:
        candidate_id: UUID of candidate
        job_posting_id: UUID of job posting
        
    Returns:
        Dict with score and explanation
    """
    url = f"{settings.backend_url}/scoring/calculate-cv-score"
    payload = {
        "candidate_id": candidate_id,
        "job_posting_id": job_posting_id
    }
    
    try:
        async with httpx.AsyncClient(timeout=settings.backend_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(
                "backend_cv_score_called",
                candidate_id=candidate_id,
                score=data.get("score")
            )
            
            return data
    
    except httpx.HTTPError as e:
        logger.error(
            "backend_cv_score_failed",
            error=str(e),
            candidate_id=candidate_id
        )
        # Return default if backend fails
        return {
            "score": 70,
            "explanation": "Score calculado localmente (backend no disponible)"
        }


async def call_backend_global_score(
    application_id: str,
    cv_score: float,
    technical_score: float,
    soft_skills_score: float
) -> Dict:
    """
    Call backend to calculate global score.
    
    Args:
        application_id: UUID of application
        cv_score: CV score (0-100)
        technical_score: Technical score (0-100)
        soft_skills_score: Soft skills score (0-100)
        
    Returns:
        Dict with global score and explanation
    """
    url = f"{settings.backend_url}/scoring/calculate-global-score"
    payload = {
        "application_id": application_id,
        "cv_score": cv_score,
        "technical_score": technical_score,
        "soft_skills_score": soft_skills_score,
        "scoring_weights": {
            "cv": 0.4,
            "technical": 0.4,
            "soft_skills": 0.2
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=settings.backend_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(
                "backend_global_score_called",
                application_id=application_id,
                global_score=data.get("global_score")
            )
            
            return data
    
    except httpx.HTTPError as e:
        logger.error(
            "backend_global_score_failed",
            error=str(e),
            application_id=application_id
        )
        # Calculate locally if backend fails
        global_score = (cv_score * 0.4) + (technical_score * 0.4) + (soft_skills_score * 0.2)
        return {
            "global_score": round(global_score, 1),
            "explanation": "Score calculado localmente"
        }


async def save_message_to_backend(application_id: str, message_data: Dict) -> bool:
    """
    Save message to backend via webhook.
    
    Args:
        application_id: UUID of application
        message_data: Message data to save
        
    Returns:
        True if successful
    """
    url = f"{settings.backend_url}/webhook/save-score"
    payload = {
        "application_id": application_id,
        **message_data
    }
    
    try:
        async with httpx.AsyncClient(timeout=settings.backend_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info("message_saved_to_backend", application_id=application_id)
            return True
    
    except httpx.HTTPError as e:
        logger.warning(
            "message_save_to_backend_failed",
            error=str(e),
            application_id=application_id
        )
        return False
