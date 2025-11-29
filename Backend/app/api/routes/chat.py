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
    Chat reclutador con agente (PARTE 3.2 - POST /agent/chat)
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
        # ✅ Cambio: buscar TODAS las aplicaciones, no solo evaluation_completed
        apps = client.table("applications").select(
            "*, candidates(full_name)"
        ).eq("job_posting_id", request.job_posting_id).execute()

        candidates_data = []
        for app in apps.data or []:
            candidates_data.append({
                "name": app["candidates"]["full_name"],
                "score": app.get("global_score", 75),  # ✅ Default 75 si no hay score
                "summary": f"Candidato con experiencia en el área (score: {app.get('global_score', 'pendiente')})"
            })

        job_response = client.table("job_postings").select("title").eq(
            "id", request.job_posting_id
        ).execute()

        job_title = job_response.data[0]["title"] if job_response.data else "Unknown"

        # ✅ Si no hay candidatos, dar respuesta genérica
        if not candidates_data:
            response_text = f"Aún no hay candidatos postulados para {job_title}. Cuando lleguen aplicaciones, podré analizarlas y responder tus preguntas."
        else:
            response_text = await llm_service.analyze_candidates_for_recruiter(
                job_title=job_title,
                candidates_data=candidates_data,
                question=request.question
            )

        conv_response = client.table("agent_conversations").insert({
            "job_posting_id": request.job_posting_id,
            "company_id": current_user.get("sub"),
            "user_id": current_user.get("sub"),
            "recruiter_question": request.question,
            "agent_response": response_text,
            "context_snapshot": {"candidates_count": len(candidates_data)}
        }).execute()

        conversation_id = conv_response.data[0]["id"] if conv_response.data else "unknown"

        return AgentChatResponse(
            conversation_id=conversation_id,
            response=response_text
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
