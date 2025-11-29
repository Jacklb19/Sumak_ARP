from fastapi import APIRouter, HTTPException, Depends
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
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        app_response = client.table("applications").select(
            "candidate_id"
        ).eq("id", request.application_id).execute()

        if not app_response.data:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        candidate_id = app_response.data[0]["candidate_id"]

        cand_resp = client.table("candidates").select(
            "full_name, email"
        ).eq("id", candidate_id).execute()

        if not cand_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        candidate = cand_resp.data[0]

        email_data = await llm_service.generate_onboarding_email(
            candidate_name=candidate["full_name"],
            job_title=request.job_info.get("title", ""),
            company_name=request.company_info.get("name", ""),
            start_date=str(datetime.now().date()),
            first_day_checklist=request.first_day_checklist or [],
            goals_30_60_90=request.goals_30_60_90 or {}
        )

        template_response = client.table("onboarding_templates").insert({
            "application_id": request.application_id,
            "recipient_email": candidate["email"],
            "recipient_name": candidate["full_name"],
            "subject": email_data["subject"],
            "body": email_data["body"],
            "status": "generated",
            "company_name": request.company_info.get("name"),
            "job_title": request.job_info.get("title"),
            "start_date": str(datetime.now().date())
        }).execute()

        template_id = template_response.data[0]["id"]

        return GenerateOnboardingResponse(
            success=True,
            onboarding_template_id=template_id,
            email_preview={
                "subject": email_data["subject"],
                "body": email_data["body"]
            },
            recipient_email=candidate["email"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/send", response_model=SendOnboardingResponse)
async def send_onboarding(
    request: SendOnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        response = client.table("onboarding_templates").update({
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat()
        }).eq("id", request.onboarding_template_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )

        template = response.data[0]

        return SendOnboardingResponse(
            success=True,
            sent_at=datetime.utcnow(),
            recipient=template["recipient_email"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
