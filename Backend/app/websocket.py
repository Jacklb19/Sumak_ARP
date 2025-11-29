"""
WebSocket para chat de entrevista en tiempo real
"""
from fastapi import WebSocket, WebSocketDisconnect, Query, status
from typing import Dict
import json
import asyncio
from datetime import datetime
import httpx
from app.core.config import settings
from app.core.supabase_client import SupabaseClient
from app.api.routes.candidates import decode_token

# Gestión de conexiones activas
active_connections: Dict[str, WebSocket] = {}


class InterviewWebSocketManager:
    """Manager para WebSocket de entrevistas"""
    
    @staticmethod
    async def verify_candidate_access(token: str, application_id: str) -> dict:
        """
        Verificar que el candidato tiene acceso a esta entrevista
        """
        client = SupabaseClient.get_client(use_service_role=True)
        
        try:
            # Decodificar token
            payload = decode_token(token)
            candidate_id = payload["sub"]
            
            # Verificar que la application pertenece al candidato
            response = client.table("applications")\
                .select("*, job_postings(title, company_id, companies(name))")\
                .eq("id", application_id)\
                .eq("candidate_id", candidate_id)\
                .execute()
            
            if not response.data:
                return None
            
            application = response.data[0]
            
            return {
                "candidate_id": candidate_id,
                "application": application
            }
        
        except Exception as e:
            print(f"Error verifying access: {str(e)}")
            return None
    
    @staticmethod
    async def save_message(application_id: str, sender: str, message_text: str, 
                          message_type: str = "answer", question_category: str = None):
        """Guardar mensaje en la base de datos"""
        client = SupabaseClient.get_client(use_service_role=True)
        
        try:
            # Obtener el último order_index
            last_msg = client.table("interview_messages")\
                .select("order_index")\
                .eq("application_id", application_id)\
                .order("order_index", desc=True)\
                .limit(1)\
                .execute()
            
            next_order = 1 if not last_msg.data else last_msg.data[0]["order_index"] + 1
            
            # Insertar mensaje
            message_data = {
                "application_id": application_id,
                "sender": sender,
                "message_text": message_text,
                "message_type": message_type,
                "question_category": question_category,
                "order_index": next_order,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            client.table("interview_messages").insert(message_data).execute()
            
        except Exception as e:
            print(f"Error saving message: {str(e)}")
    
    @staticmethod
    async def call_langgraph(application_id: str, candidate_message: str) -> dict:
        """
        Llamar a LangGraph para procesar mensaje y obtener respuesta
        """
        client = SupabaseClient.get_client(use_service_role=True)
        
        try:
            # Obtener contexto de la aplicación
            app_response = client.table("applications")\
                .select("""
                    *,
                    job_postings(*, companies(*)),
                    candidates(*)
                """)\
                .eq("id", application_id)\
                .execute()
            
            if not app_response.data:
                raise Exception("Application not found")
            
            app_data = app_response.data[0]
            
            # Obtener historial de mensajes
            messages_response = client.table("interview_messages")\
                .select("*")\
                .eq("application_id", application_id)\
                .order("order_index")\
                .execute()
            
            conversation_history = [
                {
                    "sender": msg["sender"],
                    "text": msg["message_text"],
                    "category": msg.get("question_category")
                }
                for msg in messages_response.data or []
            ]
            
            # Payload para LangGraph
            payload = {
                "application_id": application_id,
                "candidate_message": candidate_message,
                "interview_state": {
                    "job_context": {
                        "title": app_data["job_postings"]["title"],
                        "description": app_data["job_postings"]["description"],
                        "required_skills": app_data["job_postings"].get("required_skills", {}),
                    },
                    "candidate_context": {
                        "name": app_data["candidates"]["full_name"],
                        "email": app_data["candidates"]["email"],
                    },
                    "conversation_history": conversation_history,
                    "current_phase": app_data.get("current_phase", "knockout"),
                }
            }
            
            # Llamar a LangGraph
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    f"{settings.LANGGRAPH_URL}/interview-step",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Fallback: respuesta simple si LangGraph falla
                    return {
                        "should_continue": True,
                        "next_question": f"Gracias por tu respuesta. ¿Puedes contarme más sobre tu experiencia?",
                        "phase": "technical",
                        "score": None
                    }
        
        except Exception as e:
            print(f"Error calling LangGraph: {str(e)}")
            # Fallback response
            return {
                "should_continue": True,
                "next_question": "Gracias. ¿Puedes elaborar más sobre eso?",
                "phase": "technical",
                "score": None
            }
    
    @staticmethod
    async def update_application_status(application_id: str, new_status: str):
        """Actualizar estado de la aplicación"""
        client = SupabaseClient.get_client(use_service_role=True)
        
        try:
            update_data = {"status": new_status}
            
            if new_status == "interview_in_progress":
                update_data["interview_started_at"] = datetime.utcnow().isoformat()
            elif new_status == "evaluation_completed":
                update_data["interview_completed_at"] = datetime.utcnow().isoformat()
            
            client.table("applications")\
                .update(update_data)\
                .eq("id", application_id)\
                .execute()
        
        except Exception as e:
            print(f"Error updating application status: {str(e)}")


async def interview_websocket_endpoint(
    websocket: WebSocket,
    application_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint para entrevista en tiempo real
    
    URL: ws://localhost:8000/ws/interview/{application_id}?token={jwt}
    """
    manager = InterviewWebSocketManager()
    
    # Verificar acceso
    access_data = await manager.verify_candidate_access(token, application_id)
    
    if not access_data:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    active_connections[application_id] = websocket
    
    try:
        application = access_data["application"]
        job_title = application["job_postings"]["title"]
        company_name = application["job_postings"]["companies"]["name"]
        
        # Enviar mensaje de conexión
        await websocket.send_json({
            "type": "connected",
            "message": f"Conectado a la entrevista para {job_title} en {company_name}",
            "application_id": application_id
        })
        
        # Si la entrevista está en pending, enviar primera pregunta
        if application["status"] == "pending":
            await manager.update_application_status(application_id, "interview_in_progress")
            
            candidate_name = access_data.get("candidate_id", "candidato")
            first_question = f"¡Hola! 👋 Bienvenido al proceso de selección para {job_title}. Este es un proceso asistido por IA donde te haré preguntas sobre tus habilidades técnicas, experiencia y soft skills. ¿Estás listo para comenzar? Por favor responde 'Sí' cuando estés preparado."
            
            await manager.save_message(
                application_id=application_id,
                sender="agent",
                message_text=first_question,
                message_type="question",
                question_category="greeting"
            )
            
            await websocket.send_json({
                "type": "question",
                "sender": "agent",
                "message_text": first_question,
                "question_category": "greeting",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Loop principal de mensajes
        while True:
            # Recibir mensaje del candidato
            data = await websocket.receive_json()
            
            if data.get("type") == "candidate_message":
                candidate_message = data.get("message_text", "").strip()
                
                if not candidate_message:
                    continue
                
                # Guardar mensaje del candidato
                await manager.save_message(
                    application_id=application_id,
                    sender="candidate",
                    message_text=candidate_message,
                    message_type="answer"
                )
                
                # Enviar indicador de "typing..."
                await websocket.send_json({
                    "type": "typing",
                    "message": "El agente está escribiendo..."
                })
                
                # Simular delay (opcional)
                await asyncio.sleep(1)
                
                # Llamar a LangGraph para procesar
                langgraph_response = await manager.call_langgraph(
                    application_id=application_id,
                    candidate_message=candidate_message
                )
                
                # Si debe continuar, enviar siguiente pregunta
                if langgraph_response.get("should_continue", True):
                    next_question = langgraph_response.get("next_question")
                    phase = langgraph_response.get("phase", "technical")
                    
                    # Guardar pregunta del agente
                    await manager.save_message(
                        application_id=application_id,
                        sender="agent",
                        message_text=next_question,
                        message_type="question",
                        question_category=phase
                    )
                    
                    # Enviar pregunta
                    await websocket.send_json({
                        "type": "question",
                        "sender": "agent",
                        "message_text": next_question,
                        "question_category": phase,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Si hay score, enviarlo
                    if langgraph_response.get("score"):
                        await websocket.send_json({
                            "type": "score_update",
                            "score": langgraph_response["score"],
                            "explanation": langgraph_response.get("explanation", ""),
                            "question_category": phase
                        })
                
                else:
                    # Entrevista completada
                    global_score = langgraph_response.get("global_score", 0)
                    
                    completion_message = f"¡Gracias por tus respuestas! La entrevista ha finalizado. Tu puntuación global es {global_score:.1f}/100. El reclutador revisará tu evaluación y te contactará pronto."
                    
                    await manager.save_message(
                        application_id=application_id,
                        sender="agent",
                        message_text=completion_message,
                        message_type="closing",
                        question_category="closing"
                    )
                    
                    await manager.update_application_status(
                        application_id=application_id,
                        new_status="evaluation_completed"
                    )
                    
                    await websocket.send_json({
                        "type": "interview_completed",
                        "message": completion_message,
                        "global_score": global_score,
                        "redirect_to": f"/dashboard/applications/{application_id}"
                    })
                    
                    break
    
    except WebSocketDisconnect:
        print(f"Client disconnected from interview {application_id}")
        if application_id in active_connections:
            del active_connections[application_id]
    
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error en la entrevista: {str(e)}"
            })
            await websocket.close()
        except:
            pass
        if application_id in active_connections:
            del active_connections[application_id]
