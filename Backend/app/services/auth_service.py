from fastapi import HTTPException, status
from app.core.supabase_client import SupabaseClient
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.models.schemas import RegisterCompanyRequest, LoginRequest, TokenResponse
from datetime import timedelta


class AuthService:
    """Servicio de autenticación"""
    
    def __init__(self):
        # Cliente normal para operaciones de lectura
        self.supabase = SupabaseClient.get_client(use_service_role=False)
        # Cliente admin para operaciones de escritura (bypass RLS)
        self.admin_supabase = SupabaseClient.get_client(use_service_role=True)
    
    async def register_company(self, request: RegisterCompanyRequest) -> TokenResponse:
        """Registrar nueva empresa"""
        try:
            # 1. Verificar si email ya existe (con cliente normal)
            existing = self.supabase.table("companies").select("id").eq("email", request.email).execute()
            
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # 2. Hash password
            password_hash = hash_password(request.password)
            
            # 3. Crear empresa en Supabase (✅ CON CLIENTE ADMIN para bypass RLS)
            result = self.admin_supabase.table("companies").insert({
                "name": request.company_name,
                "email": request.email,
                "sector": request.sector,
                "size": request.size,
                "country": request.country,
                "password_hash": password_hash
            }).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create company"
                )
            
            company = result.data[0]
            
            # 4. Generar JWT token
            token_data = {
                "sub": company["id"],
                "email": company["email"],
                "role": "company_admin"
            }
            token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return TokenResponse(
                success=True,
                token=token,
                company_id=company["id"],
                message="Company registered successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration error: {str(e)}"
            )
    
    async def login(self, request: LoginRequest) -> TokenResponse:
        """Login de empresa"""
        try:
            # 1. Buscar empresa por email (usa cliente admin para ver password_hash)
            result = self.admin_supabase.table("companies").select("*").eq("email", request.email).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            company = result.data[0]
            
            # 2. Verificar password
            password_hash = company.get("password_hash", "")
            if not password_hash or not verify_password(request.password, password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # 3. Generar JWT token
            token_data = {
                "sub": company["id"],
                "email": company["email"],
                "role": "company_admin"
            }
            token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return TokenResponse(
                success=True,
                token=token,
                company_id=company["id"],
                message="Login successful"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login error"
            )
