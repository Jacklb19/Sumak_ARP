from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import AgentChatRequest, AgentChatResponse
from app.core.security import get_current_user
from app.services.llm_service import LLMService
from app.core.supabase_client import SupabaseClient
from typing import Dict, Any

router = APIRouter()
llm_service = LLMService()


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Chat reclutador con agente (PARTE 3.2 - POST /agent-chat)
    """
    client = SupabaseClient.get_client()
    
    try:
        # Recuperar candidatos
        apps = client.table("applications").select(
            "*, candidates(full_name)"
        ).eq("job_posting_id", request.job_posting_id).eq(
            "status", "evaluation_completed"
        ).execute()
        
        candidates_data = []
        for app in apps.data:
            candidates_data.append({
                "name": app["candidates"]["full_name"],
                "score": app.get("global_score", 0),
                "summary": app.get("global_score_explanation", "")
            })
        
        # Llamar LLM
        job_response = client.table("job_postings").select("title").eq(
            "id", request.job_posting_id
        ).execute()
        
        job_title = job_response.data[0]["title"] if job_response.data else "Unknown"
        
        response_text = await llm_service.analyze_candidates_for_recruiter(
            job_title=job_title,
            candidates_data=candidates_data,
            question=request.question
        )
        
        # Guardar en BD
        conv_response = client.table("agent_conversations").insert({
            "job_posting_id": request.job_posting_id,
            "company_id": current_user.get("sub"),
            "user_id": current_user.get("sub"),
            "recruiter_question": request.question,
            "agent_response": response_text,
            "context_snapshot": {"candidates_count": len(candidates_data)}
        }).execute()
        
        return {
            "conversation_id": conv_response.data[0]["id"] if conv_response.data else "unknown",
            "response": response_text
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )