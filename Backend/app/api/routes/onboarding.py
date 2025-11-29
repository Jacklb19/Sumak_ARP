from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import (
    GenerateOnboardingRequest, GenerateOnboardingResponse,
    SendOnboardingRequest, SendOnboardingResponse
)
from app.core.security import get_current_user
from app.services.llm_service import LLMService
from app.core.supabase_client import SupabaseClient
from typing import Dict, Any
from datetime import datetime

router = APIRouter()
llm_service = LLMService()


@router.post("/generate", response_model=GenerateOnboardingResponse)
async def generate_onboarding(
    request: GenerateOnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generar email de onboarding (PARTE 3.2 - POST /onboarding/generate)
    """
    client = SupabaseClient.get_client()
    
    try:
        # Recuperar datos
        app_response = client.table("applications").select(
            "*, candidates(full_name, email)"
        ).eq("id", request.application_id).execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app = app_response.data[0]
        
        # Generar email
        email_data = await llm_service.generate_onboarding_email(
            candidate_name=app["candidates"]["full_name"],
            job_title=request.job_info.get("title", ""),
            company_name=request.company_info.get("name", ""),
            start_date=str(datetime.now().date()),
            first_day_checklist=request.first_day_checklist,
            goals_30_60_90=request.goals_30_60_90
        )
        
        # Guardar template
        template_response = client.table("onboarding_templates").insert({
            "application_id": request.application_id,
            "recipient_email": app["candidates"]["email"],
            "recipient_name": app["candidates"]["full_name"],
            "subject": email_data["subject"],
            "body": email_data["body"],
            "status": "generated",
            "company_name": request.company_info.get("name"),
            "job_title": request.job_info.get("title"),
            "start_date": str(datetime.now().date())
        }).execute()
        
        return {
            "success": True,
            "onboarding_template_id": template_response.data[0]["id"],
            "email_preview": {
                "subject": email_data["subject"],
                "body": email_data["body"]
            },
            "recipient_email": app["candidates"]["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/send", response_model=SendOnboardingResponse)
async def send_onboarding(
    request: SendOnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Enviar email de onboarding (PARTE 3.2 - POST /onboarding/send)
    """
    client = SupabaseClient.get_client()
    
    try:
        # Actualizar status
        response = client.table("onboarding_templates").update({
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat()
        }).eq("id", request.onboarding_template_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template = response.data[0]
        
        # TODO: Enviar email real con SendGrid
        
        return {
            "success": True,
            "sent_at": datetime.utcnow(),
            "recipient": template["recipient_email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )