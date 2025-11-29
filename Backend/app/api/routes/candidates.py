"""
Rutas para autenticación y gestión de candidatos
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
from app.core.config import settings
from app.core.supabase_client import SupabaseClient

router = APIRouter()
security = HTTPBearer()


# ============================================================
# SCHEMAS
# ============================================================

class CandidateRegisterSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    country: str = Field(default="Colombia", max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v

class CandidateLoginSchema(BaseModel):
    email: EmailStr
    password: str

class CandidateUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    seniority_level: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class TokenResponse(BaseModel):
    success: bool
    token: str
    candidate_id: str
    full_name: str
    message: str

class CandidateResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone_number: str
    country: str
    city: Optional[str]
    seniority_level: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    created_at: datetime



# ============================================================
# UTILITIES
# ============================================================

def hash_password(password: str) -> str:
    """Hash password con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(candidate_id: str, email: str) -> str:
    """Crear JWT token"""
    payload = {
        "sub": candidate_id,
        "email": email,
        "type": "candidate",
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodificar JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_candidate(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency para obtener candidato actual desde token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as candidate"
        )
    
    client = SupabaseClient.get_client(use_service_role=True)
    
    try:
        response = client.table("candidates").select("*").eq("id", payload["sub"]).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching candidate: {str(e)}"
        )


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/register-candidate", response_model=TokenResponse)
async def register_candidate(data: CandidateRegisterSchema):
    """
    Registrar nuevo candidato
    """
    client = SupabaseClient.get_client(use_service_role=True)
    
    try:
        # 1. Verificar si email ya existe
        existing = client.table("candidates").select("id").eq("email", data.email).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 2. Hash password
        hashed_pw = hash_password(data.password)
        
        # 3. Crear candidato en Supabase
        candidate_data = {
            "full_name": data.full_name,
            "email": data.email,
            "phone_number": data.phone_number,
            "password_hash": hashed_pw,
            "country": data.country,
            "city": data.city,
            "seniority_level": "junior",
        }
        
        response = client.table("candidates").insert(candidate_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create candidate"
            )
        
        candidate = response.data[0]
        
        # 4. Generar JWT token
        token = create_access_token(candidate["id"], candidate["email"])
        
        return TokenResponse(
            success=True,
            token=token,
            candidate_id=candidate["id"],
            full_name=candidate["full_name"],
            message="Candidate registered successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login-candidate", response_model=TokenResponse)
async def login_candidate(credentials: CandidateLoginSchema):
    """
    Login de candidato
    """
    client = SupabaseClient.get_client(use_service_role=True)
    
    try:
        # 1. Buscar candidato por email
        response = client.table("candidates").select("*").eq("email", credentials.email).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        candidate = response.data[0]
        
        # 2. Verificar password
        if not verify_password(credentials.password, candidate["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # 3. Generar token
        token = create_access_token(candidate["id"], candidate["email"])
        
        return TokenResponse(
            success=True,
            token=token,
            candidate_id=candidate["id"],
            full_name=candidate["full_name"],
            message="Login successful"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=CandidateResponse)
async def get_current_user(current_candidate: dict = Depends(get_current_candidate)):
    """
    Obtener datos del candidato actual
    """
    return CandidateResponse(**current_candidate)


@router.put("/me", response_model=CandidateResponse)
async def update_candidate_profile(
    data: CandidateUpdateSchema,
    current_candidate: dict = Depends(get_current_candidate)
):
    """
    Actualizar perfil del candidato
    """
    client = SupabaseClient.get_client(use_service_role=True)
    
    try:
        # Construir objeto de actualización solo con campos no nulos
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )
        
        # Actualizar en Supabase
        response = client.table("candidates")\
            .update(update_data)\
            .eq("id", current_candidate["id"])\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        return CandidateResponse(**response.data[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}"
        )


@router.get("/my-applications")
async def get_my_applications(current_candidate: dict = Depends(get_current_candidate)):
    """
    Obtener todas las postulaciones del candidato actual
    """
    client = SupabaseClient.get_client(use_service_role=True)
    
    try:
        response = client.table("applications")\
            .select("""
                *,
                job_postings!inner(id, title, company_id, companies!inner(name, logo_url))
            """)\
            .eq("candidate_id", current_candidate["id"])\
            .order("created_at", desc=True)\
            .execute()
        
        # Formatear respuesta
        applications = []
        for app in response.data or []:
            job = app.get("job_postings", {})
            company = job.get("companies", {})
            
            applications.append({
                "id": app["id"],
                "job_posting_id": app["job_posting_id"],
                "job_title": job.get("title", "Unknown"),
                "company_name": company.get("name", "Unknown"),
                "company_logo": company.get("logo_url"),
                "status": app["status"],
                "global_score": app.get("global_score", 0),
                "cv_score": app.get("cv_score"),
                "technical_score": app.get("technical_score"),
                "soft_skills_score": app.get("soft_skills_score"),
                "created_at": app["created_at"],
                "interview_started_at": app.get("interview_started_at"),
                "interview_completed_at": app.get("interview_completed_at")
            })
        
        return {
            "total": len(applications),
            "applications": applications
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )
