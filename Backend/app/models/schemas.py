from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.enums import (
    ApplicationStatus, JobPostingStatus, HiringDecision,
    SeniorityLevel, ContractType, Modality, QuestionCategory, InterviewPhase
)


# ============================================================
# AUTH SCHEMAS
# ============================================================

class RegisterCompanyRequest(BaseModel):
    """Registro de empresa"""
    company_name: str
    email: EmailStr
    password: str
    sector: Optional[str] = None
    size: Optional[str] = None
    country: Optional[str] = None


class LoginRequest(BaseModel):
    """Login de empresa"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Respuesta de token"""
    success: bool
    token: str
    company_id: str
    user_role: str = "admin"
    message: Optional[str] = None


# ============================================================
# COMPANY SCHEMAS
# ============================================================

class CompanyResponse(BaseModel):
    """Respuesta de empresa"""
    id: str
    name: str
    email: str
    sector: Optional[str]
    size: Optional[str]
    country: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    whatsapp_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateCompanyRequest(BaseModel):
    """Actualizar empresa"""
    description: Optional[str] = None
    whatsapp_number: Optional[str] = None
    whatsapp_token: Optional[str] = None
    sector: Optional[str] = None
    logo_url: Optional[str] = None


# ============================================================
# JOB POSTING SCHEMAS
# ============================================================

class CreateJobPostingRequest(BaseModel):
    """Crear vacante"""
    company_id: str
    title: str
    description: str
    area: Optional[str] = None
    contract_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    modality: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[Dict[str, Any]] = None
    nice_to_have_skills: Optional[Dict[str, Any]] = None
    custom_questions: Optional[List[str]] = None
    knockout_criteria: Optional[Dict[str, Any]] = None


class JobPostingResponse(BaseModel):
    """Respuesta de vacante"""
    id: str
    company_id: str
    title: str
    description: str
    area: Optional[str]
    contract_type: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    modality: Optional[str]
    location: Optional[str]
    required_skills: Optional[Dict[str, Any]]
    nice_to_have_skills: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class PublishJobPostingRequest(BaseModel):
    """Publicar vacante"""
    pass


# ============================================================
# CANDIDATE SCHEMAS
# ============================================================

class CandidateResponse(BaseModel):
    """Respuesta de candidato"""
    id: str
    email: str
    phone_number: str
    full_name: str
    country: Optional[str]
    city: Optional[str]
    seniority_level: Optional[str]
    expected_salary: Optional[int]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# APPLICATION / POSTULACIÓN SCHEMAS
# ============================================================

class CreateApplicationRequest(BaseModel):
    """Crear postulación"""
    full_name: str
    email: EmailStr
    phone_number: str
    country: Optional[str] = None
    city: Optional[str] = None
    seniority_level: Optional[str] = None
    expected_salary: Optional[int] = None
    job_posting_id: str
    preferred_channel: str = "whatsapp"  # whatsapp, telegram, web
    consent_ai: bool
    consent_data_storage: bool
    # cv_file será enviado como multipart/form-data


class ApplicationResponse(BaseModel):
    """Respuesta de postulación"""
    id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    job_posting_id: str
    job_title: str
    status: str
    cv_score: Optional[float]
    technical_score: Optional[float]
    soft_skills_score: Optional[float]
    global_score: Optional[float]
    interview_started_at: Optional[datetime]
    interview_completed_at: Optional[datetime]
    interview_duration_minutes: Optional[int]
    hiring_decision: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    """Lista de aplicaciones"""
    total: int
    applications: List[ApplicationResponse]


# ============================================================
# INTERVIEW MESSAGE SCHEMAS
# ============================================================

class InterviewMessageResponse(BaseModel):
    """Mensaje de entrevista"""
    order: int
    sender: str
    timestamp: datetime
    message_text: str
    question_category: Optional[str]
    agent_score: Optional[float]
    agent_scoring_explanation: Optional[str]


class InterviewTranscriptResponse(BaseModel):
    """Transcripción completa"""
    application_id: str
    messages: List[InterviewMessageResponse]


# ============================================================
# SCORING SCHEMAS
# ============================================================

class CalculateCVScoreRequest(BaseModel):
    """Calcular score de CV"""
    candidate_id: str
    job_posting_id: str


class CVScoreResponse(BaseModel):
    """Respuesta de score de CV"""
    score: float
    sub_scores: Optional[Dict[str, float]]
    explanation: str


class CalculateGlobalScoreRequest(BaseModel):
    """Calcular score global"""
    application_id: str
    job_posting_id: str
    cv_score: float
    technical_score: float
    soft_skills_score: float
    scoring_weights: Optional[Dict[str, float]] = None


class GlobalScoreResponse(BaseModel):
    """Respuesta de score global"""
    global_score: float
    explanation: str


# ============================================================
# WEBHOOK SCHEMAS (n8n)
# ============================================================

class InterviewStepRequest(BaseModel):
    """Request para webhook interview-step"""
    application_id: str
    candidate_message: str
    interview_state: Dict[str, Any]


class InterviewStepResponse(BaseModel):
    """Response del webhook interview-step"""
    success: bool
    message: str


# ============================================================
# CHAT AGENT SCHEMAS
# ============================================================

class AgentChatRequest(BaseModel):
    """Chat con agente analista"""
    job_posting_id: str
    question: str


class AgentChatResponse(BaseModel):
    """Respuesta del agente"""
    conversation_id: str
    response: str


# ============================================================
# HIRING SCHEMAS
# ============================================================

class HireApplicationRequest(BaseModel):
    """Contratar candidato"""
    hire_date: date
    job_title_override: Optional[str] = None
    department: Optional[str] = None
    manager_name: Optional[str] = None
    start_time: Optional[str] = None
    work_schedule: Optional[str] = None


class HireApplicationResponse(BaseModel):
    """Respuesta de contratación"""
    success: bool
    application_id: str
    status: str
    message: str


# ============================================================
# ONBOARDING SCHEMAS
# ============================================================

class GenerateOnboardingRequest(BaseModel):
    """Generar email de inducción"""
    application_id: str
    company_info: Dict[str, Any]
    job_info: Dict[str, Any]
    first_day_checklist: Optional[Dict[str, Any]] = None
    goals_30_60_90: Optional[Dict[str, Any]] = None


class OnboardingEmailPreview(BaseModel):
    """Preview del email"""
    subject: str
    body: str


class GenerateOnboardingResponse(BaseModel):
    """Respuesta de generación"""
    success: bool
    onboarding_template_id: str
    email_preview: OnboardingEmailPreview
    recipient_email: str


class SendOnboardingRequest(BaseModel):
    """Enviar email de inducción"""
    onboarding_template_id: str


class SendOnboardingResponse(BaseModel):
    """Respuesta de envío"""
    success: bool
    sent_at: datetime
    recipient: str


# ============================================================
# GENERIC RESPONSES
# ============================================================

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """Respuesta genérica de éxito"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None