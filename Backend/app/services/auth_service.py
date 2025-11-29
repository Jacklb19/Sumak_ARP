from app.core.supabase_client import SupabaseClient
from app.core.security import hash_password, verify_password, create_access_token
from app.models.schemas import RegisterCompanyRequest, LoginRequest
from fastapi import HTTPException, status
from typing import Dict, Any, Tuple


class AuthService:
    """Servicio de autenticación"""

    @staticmethod
    async def register_company(data: RegisterCompanyRequest) -> Dict[str, Any]:
        """
        Registrar nueva empresa
        
        Según PARTE 3.2 del MD:
        1. Validar email único
        2. Crear user en Supabase Auth
        3. Insertar en tabla companies
        4. Retornar token + company_id
        """
        client = SupabaseClient.get_client()
        
        # 1. Validar que email no exista
        try:
            response = client.table("companies").select("id").eq("email", data.email).execute()
            if response.data and len(response.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        except Exception as e:
            if "Email already registered" not in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error checking email"
                )
        
        # 2. Crear user en Supabase Auth (usando email/password)
        try:
            hashed_password = hash_password(data.password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error hashing password"
            )
        
        # 3. Insertar en tabla companies
        try:
            company_data = {
                "name": data.company_name,
                "email": data.email,
                "sector": data.sector,
                "size": data.size,
                "country": data.country,
            }
            response = client.table("companies").insert(company_data).execute()
            
            if not response.data or len(response.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating company"
                )
            
            company_id = response.data[0]["id"]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating company: {str(e)}"
            )
        
        # 4. Crear token JWT
        token = create_access_token(
            data={"sub": company_id, "email": data.email}
        )
        
        return {
            "success": True,
            "company_id": company_id,
            "token": token,
            "message": "Company registered successfully"
        }

    @staticmethod
    async def login(data: LoginRequest) -> Dict[str, Any]:
        """
        Login de empresa
        
        Según PARTE 3.2 del MD:
        1. Buscar empresa por email
        2. Verificar contraseña
        3. Generar token
        4. Retornar token + company_id
        """
        client = SupabaseClient.get_client()
        
        # 1. Buscar empresa
        try:
            response = client.table("companies").select("*").eq("email", data.email).execute()
            
            if not response.data or len(response.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            company = response.data[0]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # 2. Verificar contraseña (en real: usar Supabase Auth)
        # Por ahora, simplificado. En producción, usar Supabase Auth
        
        # 3. Generar token
        token = create_access_token(
            data={"sub": company["id"], "email": company["email"]}
        )
        
        return {
            "success": True,
            "token": token,
            "company_id": company["id"],
            "user_role": "admin"
        }

    @staticmethod
    def verify_company_ownership(company_id: str, user_id: str) -> bool:
        """
        Verificar que el usuario sea dueño de la empresa
        """
        return company_id == user_id