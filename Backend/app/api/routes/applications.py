from fastapi import (
    APIRouter, HTTPException, Depends,
    UploadFile, File, Query, Form
)
from app.models.schemas import (
    ApplicationResponse, ApplicationListResponse,
    InterviewTranscriptResponse, HireApplicationRequest, HireApplicationResponse
)
from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.services.cv_parser import CVParserService
from typing import Dict, Any, Optional
from datetime import datetime


router = APIRouter()
cv_parser = CVParserService()


@router.post("/", response_model=Dict[str, Any])
async def create_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    job_posting_id: str = Form(...),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    seniority_level: Optional[str] = Form(None),
    expected_salary: Optional[int] = Form(None),
    cv_file: UploadFile = File(...),
    consent_ai: str = Form(...),
    consent_data_storage: str = Form(...)
):
    """
    Crear postulación con CV (PARTE 3.2 - POST /applications)
    Compatible con test_backend.py (multipart/form-data).
    """

    def parse_bool(value: str) -> bool:
        return value.lower() in ["true", "1", "yes", "y", "on"]

    if not parse_bool(consent_ai) or not parse_bool(consent_data_storage):
        raise HTTPException(
            status_code=400,
            detail="Consent is required"
        )

    # Usa service_role para evitar problemas de RLS
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        # 1. Parsear CV (texto + embedding)
        cv_text, cv_embedding = await cv_parser.parse_cv_file(cv_file)

        # 2. Obtener company_id de la vacante
        job_resp = client.table("job_postings").select("company_id").eq(
            "id", job_posting_id
        ).execute()
        if not job_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Job posting not found"
            )
        company_id = job_resp.data[0]["company_id"]

        # 3. Crear/actualizar candidato (upsert por email)
        candidate_response = client.table("candidates").upsert({
            "email": email,
            "phone_number": phone_number,
            "full_name": full_name,
            "country": country,
            "city": city,
            "seniority_level": seniority_level,
            "expected_salary": expected_salary,
            "cv_text_extracted": cv_text,
            #"cv_embedding": cv_embedding
        }).execute()

        if not candidate_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error creating candidate"
            )

        candidate_id = candidate_response.data[0]["id"]

        # 4. Crear application
        app_response = client.table("applications").insert({
            "candidate_id": candidate_id,
            "job_posting_id": job_posting_id,
            "company_id": company_id,
            "status": "pending",
            "cv_file_url": f"cvs/{candidate_id}/{job_posting_id}.pdf"
        }).execute()

        if not app_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error creating application"
            )

        application_id = app_response.data[0]["id"]

        return {
            "success": True,
            "application_id": application_id,
            "candidate_id": candidate_id,
            "status": "pending",
            "message": "Application submitted. Interview will start via WhatsApp shortly."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating application: {str(e)}"
        )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener detalle de aplicación (PARTE 3.2 - GET /applications/:id)
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        app_resp = client.table("applications").select("*").eq(
            "id", application_id
        ).execute()

        if not app_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        app = app_resp.data[0]

        cand_resp = client.table("candidates").select(
            "full_name, email"
        ).eq("id", app["candidate_id"]).execute()

        job_resp = client.table("job_postings").select(
            "title"
        ).eq("id", app["job_posting_id"]).execute()

        candidate = cand_resp.data[0] if cand_resp.data else {"full_name": "", "email": ""}
        job = job_resp.data[0] if job_resp.data else {"title": ""}

        return {
            "id": app["id"],
            "candidate_id": app["candidate_id"],
            "candidate_name": candidate["full_name"],
            "candidate_email": candidate["email"],
            "job_posting_id": app["job_posting_id"],
            "job_title": job["title"],
            "status": app["status"],
            "cv_score": app.get("cv_score"),
            "technical_score": app.get("technical_score"),
            "soft_skills_score": app.get("soft_skills_score"),
            "global_score": app.get("global_score"),
            "interview_started_at": app.get("interview_started_at"),
            "interview_completed_at": app.get("interview_completed_at"),
            "interview_duration_minutes": app.get("interview_duration_minutes"),
            "hiring_decision": app.get("hiring_decision"),
            "created_at": app["created_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{application_id}/transcript", response_model=InterviewTranscriptResponse)
async def get_interview_transcript(application_id: str):
    """
    Obtener transcripción de entrevista (PARTE 3.2 - GET /applications/:id/transcript)
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        response = client.table("interview_messages").select("*").eq(
            "application_id", application_id
        ).order("order_index", desc=False).execute()

        messages = []
        for msg in response.data or []:
            messages.append({
                "order": msg.get("order_index"),
                "sender": msg.get("sender"),
                "timestamp": msg.get("timestamp"),
                "message_text": msg.get("message_text"),
                "question_category": msg.get("question_category"),
                "agent_score": msg.get("agent_score"),
                "agent_scoring_explanation": msg.get("agent_scoring_explanation")
            })

        return {
            "application_id": application_id,
            "messages": messages
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("", response_model=ApplicationListResponse)
async def list_applications_by_job(
    job_posting_id: str = Query(...),
    status: Optional[str] = Query(None),
    sort_by: str = Query("global_score"),
    sort_order: str = Query("desc"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Listar candidatos de una vacante (PARTE 3.2 - GET /job-postings/:id/applications)
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        query = client.table("applications").select(
            "*, candidates(full_name, email)"
        ).eq("job_posting_id", job_posting_id)

        if status:
            query = query.eq("status", status)

        query = query.order(sort_by, desc=(sort_order == "desc"))
        response = query.execute()

        applications = []
        for app in response.data or []:
            applications.append({
                "id": app["id"],
                "candidate_id": app["candidate_id"],
                "candidate_name": app["candidates"]["full_name"],
                "candidate_email": app["candidates"]["email"],
                "job_posting_id": app["job_posting_id"],
                "job_title": "",
                "status": app["status"],
                "cv_score": app.get("cv_score"),
                "technical_score": app.get("technical_score"),
                "soft_skills_score": app.get("soft_skills_score"),
                "global_score": app.get("global_score"),
                "interview_started_at": app.get("interview_started_at"),
                "interview_completed_at": app.get("interview_completed_at"),
                "interview_duration_minutes": app.get("interview_duration_minutes"),
                "hiring_decision": app.get("hiring_decision"),
                "created_at": app["created_at"]
            })

        return {
            "total": len(applications),
            "applications": applications
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{application_id}/hire", response_model=HireApplicationResponse)
async def hire_application(
    application_id: str,
    request: HireApplicationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Contratar candidato (PARTE 3.2 - POST /applications/:id/hire)
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        response = client.table("applications").update({
            "status": "hired",
            "hiring_decision": "hired",
            "hire_date": request.hire_date.isoformat()
        }).eq("id", application_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        return {
            "success": True,
            "application_id": application_id,
            "status": "hired",
            "message": "Candidate hired successfully. Onboarding email will be generated."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
