from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import CompanyResponse, UpdateCompanyRequest, SuccessResponse
from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from typing import Dict, Any

router = APIRouter()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Obtener datos de empresa
    
    Según PARTE 3.2 del MD - GET /company/:company_id
    """
    client = SupabaseClient.get_client()
    
    try:
        response = client.table("companies").select("*").eq("id", company_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving company: {str(e)}"
        )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    request: UpdateCompanyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Actualizar empresa
    
    Según PARTE 3.2 del MD - PUT /company/:company_id
    """
    # Verificar que sea el dueño
    if current_user.get("sub") != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    client = SupabaseClient.get_client()
    
    try:
        # Preparar datos a actualizar
        update_data = {}
        if request.description is not None:
            update_data["description"] = request.description
        if request.whatsapp_number is not None:
            update_data["whatsapp_number"] = request.whatsapp_number
        if request.whatsapp_token is not None:
            update_data["whatsapp_token"] = request.whatsapp_token
        if request.sector is not None:
            update_data["sector"] = request.sector
        if request.logo_url is not None:
            update_data["logo_url"] = request.logo_url
        
        update_data["updated_at"] = "now()"
        
        response = client.table("companies").update(update_data).eq("id", company_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company: {str(e)}"
        )