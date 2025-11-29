from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import CompanyResponse, UpdateCompanyRequest
from app.core.supabase_client import SupabaseClient
from app.core.security import get_current_user

router = APIRouter()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, current_user: dict = Depends(get_current_user)):
    """
    Obtener perfil de empresa
    
    Según PARTE 3.2 del MD - GET /companies/{company_id}
    """
    try:
        client = SupabaseClient.get_client(use_service_role=True)
        
        result = client.table("companies").select("*").eq("id", company_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        company = result.data[0]
        
        return CompanyResponse(
            id=company["id"],
            name=company["name"],
            email=company["email"],
            sector=company.get("sector"),
            size=company.get("size"),
            country=company.get("country"),
            description=company.get("description"),
            logo_url=company.get("logo_url"),
            whatsapp_number=company.get("whatsapp_number"),
            created_at=company["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching company: {str(e)}"
        )


@router.put("/{company_id}")
async def update_company(
    company_id: str,
    request: UpdateCompanyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar perfil de empresa
    
    Según PARTE 3.2 del MD - PUT /companies/{company_id}
    """
    try:
        # Verificar que el usuario actual sea de esta empresa
        if current_user.get("sub") != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this company"
            )
        
        client = SupabaseClient.get_client(use_service_role=True)
        
        # Preparar datos para actualizar (solo campos no None)
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
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Actualizar
        result = client.table("companies").update(update_data).eq("id", company_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {
            "success": True,
            "message": "Company updated successfully",
            "data": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company: {str(e)}"
        )
