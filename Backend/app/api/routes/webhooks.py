from fastapi import APIRouter, HTTPException
from app.models.schemas import InterviewStepRequest, InterviewStepResponse
from app.core.supabase_client import SupabaseClient
from datetime import datetime

router = APIRouter()


@router.post("/interview-step", response_model=InterviewStepResponse)
async def webhook_interview_step(request: InterviewStepRequest):
    """
    Webhook para n8n - guarda mensaje del candidato.
    """
    client = SupabaseClient.get_client(use_service_role=True)

    try:
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
                status_code=500,
                detail="Error saving message"
            )

        return InterviewStepResponse(
            success=True,
            message="Message saved. LangGraph will process."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
