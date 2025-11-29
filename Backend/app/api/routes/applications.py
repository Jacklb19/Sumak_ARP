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

    # DEBUG: log de entrada
    print("\n===== DEBUG create_application START =====")
    print("full_name:", full_name)
    print("email:", email)
    print("phone_number:", phone_number)
    print("job_posting_id:", job_posting_id)
    print("country:", country)
    print("city:", city)
    print("seniority_level:", seniority_level)
    print("expected_salary:", expected_salary)
    print("consent_ai:", consent_ai)
    print("consent_data_storage:", consent_data_storage)
    print("cv_file:", cv_file.filename if cv_file else None)

    if not parse_bool(consent_ai) or not parse_bool(consent_data_storage):
        print("DEBUG: consent failed")
        raise HTTPException(
            status_code=400,
            detail="Consent is required"
        )

    client = SupabaseClient.get_client(use_service_role=True)

    try:
        # 1. Parsear CV
        print("DEBUG: before cv_parser.parse_cv_file")
        cv_text, cv_embedding = await cv_parser.parse_cv_file(cv_file)
        print("DEBUG: after cv_parser, text_len:", len(cv_text))

        # 2. Obtener company_id
        print("DEBUG: fetching job_posting company_id")
        job_resp = client.table("job_postings").select("company_id").eq(
            "id", job_posting_id
        ).execute()
        print("DEBUG job_resp.data:", job_resp.data)

        if not job_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Job posting not found"
            )
        company_id = job_resp.data[0]["company_id"]

        # 3. Upsert candidato
        print("DEBUG: upserting candidate")
        candidate_response = client.table("candidates").upsert(
            {
                "email": email,
                "phone_number": phone_number,
                "full_name": full_name,
                "country": country,
                "city": city,
                "seniority_level": seniority_level,
                "expected_salary": expected_salary,
                "cv_text_extracted": cv_text,
                # "cv_embedding": cv_embedding
            },
            on_conflict="email",
        ).execute()
        print("DEBUG candidate_response.data:", candidate_response.data)

        if not candidate_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error creating candidate"
            )

        candidate_id = candidate_response.data[0]["id"]

        # 4. Crear application
        print("DEBUG: inserting application")
        app_response = client.table("applications").insert({
            "candidate_id": candidate_id,
            "job_posting_id": job_posting_id,
            "company_id": company_id,
            "status": "pending",
            "cv_file_url": f"cvs/{candidate_id}/{job_posting_id}.pdf"
        }).execute()
        print("DEBUG app_response.data:", app_response.data)

        if not app_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error creating application"
            )

        application_id = app_response.data[0]["id"]

        print("===== DEBUG create_application OK =====\n")
        return {
            "success": True,
            "application_id": application_id,
            "candidate_id": candidate_id,
            "status": "pending",
            "message": "Application submitted. Interview will start via WhatsApp shortly."
        }

    except HTTPException:
        # ya tiene mensaje claro, solo logueamos
        import traceback
        print("===== HTTPException in create_application =====")
        traceback.print_exc()
        raise
    except Exception as e:
        import traceback
        print("===== EXCEPTION in create_application =====")
        traceback.print_exc()
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
