# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import RegisterCompanyRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()  # ✅ Esta es la línea que faltaba
auth_service = AuthService()


@router.post("/register-company", response_model=TokenResponse)
async def register_company(request: RegisterCompanyRequest):
    """
    Registrar nueva empresa
    
    Según PARTE 3.2 del MD - POST /auth/register-company
    """
    try:
        result = await auth_service.register_company(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login de empresa
    
    Según PARTE 3.2 del MD - POST /auth/login
    """
    try:
        result = await auth_service.login(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
