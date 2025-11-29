from fastapi import APIRouter, HTTPException, status
from app.models.schemas import InterviewStepRequest, InterviewStepResponse
from app.core.supabase_client import SupabaseClient
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.post("/interview-step", response_model=InterviewStepResponse)
async def webhook_interview_step(request: InterviewStepRequest):
    """
    Recibir respuesta de candidato (PARTE 3.2 - POST /webhook/interview-step)
    
    Llamado por n8n cuando candidato responde en WhatsApp
    """
    client = SupabaseClient.get_client()
    
    try:
        # Guardar mensaje
        message_data = {
            "application_id": request.application_id,
            "sender": "candidate",
            "message_text": request.candidate_message,
            "message_type": "answer",
            "question_category": request.interview_state.get("current_phase"),
            "order_index": len(request.interview_state.get("conversation_history", [])) + 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.table("interview_messages").insert(message_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving message"
            )
        
        return {
            "success": True,
            "message": "Message saved. LangGraph will process."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )