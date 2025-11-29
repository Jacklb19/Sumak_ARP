from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.schemas import (
    CreateJobPostingRequest, JobPostingResponse, SuccessResponse,
    ApplicationListResponse
)
from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.services.llm_service import LLMService
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter()
llm_service = LLMService()


@router.post("/", response_model=SuccessResponse)
async def create_job_posting(
    request: CreateJobPostingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Crear nueva vacante (PARTE 3.2 del MD - POST /job-postings)
    
    1. Validar que company_id perteneza al usuario
    2. Generar job_template_context con LLM
    3. Guardar en BD con status='draft'
    """
    # Verificar ownership
    if current_user.get("sub") != request.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    client = SupabaseClient.get_client()
    
    try:
        # 1. Generar contexto con LLM
        job_template_context = await llm_service.generate_job_context(
            job_title=request.title,
            job_description=request.description,
            required_skills=request.required_skills
        )
        
        # 2. Preparar datos
        job_data = {
            "company_id": request.company_id,
            "title": request.title,
            "description": request.description,
            "area": request.area,
            "contract_type": request.contract_type,
            "salary_min": request.salary_min,
            "salary_max": request.salary_max,
            "modality": request.modality,
            "location": request.location,
            "required_skills": request.required_skills,
            "nice_to_have_skills": request.nice_to_have_skills,
            "custom_questions": request.custom_questions,
            "knockout_criteria": request.knockout_criteria,
            "job_template_context": job_template_context,
            "status": "draft"
        }
        
        # 3. Guardar en BD
        response = client.table("job_postings").insert(job_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating job posting"
            )
        
        return {
            "success": True,
            "message": "Job posting created successfully",
            "data": {
                "job_posting_id": response.data[0]["id"],
                "status": "draft"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job_posting(job_id: str):
    """
    Obtener detalle de vacante (PARTE 3.2 - GET /job-postings/:id)
    """
    client = SupabaseClient.get_client()
    
    try:
        response = client.table("job_postings").select("*").eq("id", job_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=Dict[str, Any])
async def list_job_postings(
    status: Optional[str] = Query(None),
    company_id: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Listar vacantes (PARTE 3.2 - GET /job-postings)
    
    Filtros: status, company_id, area, modality, location
    """
    client = SupabaseClient.get_client()
    
    try:
        query = client.table("job_postings").select("*")
        
        # Filtros
        if status:
            query = query.eq("status", status)
        else:
            # Si no especifica status, mostrar solo published
            query = query.eq("status", "published")
        
        if company_id:
            query = query.eq("company_id", company_id)
        
        if area:
            query = query.eq("area", area)
        
        if modality:
            query = query.eq("modality", modality)
        
        if location:
            query = query.ilike("location", f"%{location}%")
        
        # Paginación
        response = query.range(offset, offset + limit - 1).execute()
        
        # Total count
        count_response = client.table("job_postings").select("id", count="exact").execute()
        total = count_response.count or 0
        
        return {
            "total": total,
            "postings": response.data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{job_id}/publish", response_model=SuccessResponse)
async def publish_job_posting(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Publicar vacante (PARTE 3.2 - PUT /job-postings/:id/publish)
    
    Cambiar status de 'draft' a 'published'
    """
    client = SupabaseClient.get_client()
    
    try:
        # 1. Verificar que existe y pertenece al usuario
        response = client.table("job_postings").select("company_id").eq("id", job_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )
        
        if response.data[0]["company_id"] != current_user.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # 2. Publicar
        update_response = client.table("job_postings").update({
            "status": "published",
            "published_at": datetime.utcnow().isoformat()
        }).eq("id", job_id).execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error publishing job posting"
            )
        
        return {
            "success": True,
            "message": "Job posting published successfully",
            "data": {
                "job_posting_id": job_id,
                "status": "published"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/company/{company_id}/jobs", response_model=Dict[str, Any])
async def get_company_jobs(
    company_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener todas las vacantes de una empresa (PARTE 3.2)
    """
    # Verificar ownership
    if current_user.get("sub") != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    client = SupabaseClient.get_client()
    
    try:
        response = client.table("job_postings").select("*").eq("company_id", company_id).execute()
        
        return {
            "total": len(response.data),
            "postings": response.data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )