from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt 
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.config import settings
from typing import Optional, Dict, Any


# Security bearer
security = HTTPBearer()


# ============================================================
# PASSWORD HASHING (con bcrypt directo)
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash password usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña como string
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si la contraseña coincide con el hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en BD
        
    Returns:
        True si coincide, False si no
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_bytes)


# ============================================================
# JWT TOKEN MANAGEMENT
# ============================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crear JWT token
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": company_id, "role": "admin"})
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verificar y decodificar JWT token
    
    Args:
        token: Token JWT
        
    Returns:
        Payload decodificado del token
        
    Raises:
        HTTPException: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(credentials = Depends(security)) -> Dict[str, Any]:
    """
    Obtener usuario actual desde token (Dependency para rutas protegidas)
    
    Args:
        credentials: Credenciales HTTP Bearer extraídas del header
        
    Returns:
        Payload del token con información del usuario
        
    Raises:
        HTTPException: Si el token es inválido
        
    Uso:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            company_id = current_user["sub"]
            return {"message": f"Hello company {company_id}"}
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    # Validar que el token contenga el subject (user_id/company_id)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


async def get_current_company_id(current_user: Dict = Depends(get_current_user)) -> str:
    """
    Obtener solo el company_id del usuario actual (helper)
    
    Returns:
        Company ID como string
    """
    return current_user["sub"]
