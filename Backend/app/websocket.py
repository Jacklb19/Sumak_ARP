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
import traceback


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
        client = SupabaseClient.get_client(use_service_role=True)

        try:
            # 1. Cargar application + candidate + job_posting
            app_resp = client.table("applications").select("*").eq("id", application_id).execute()
            if not app_resp.data:
                raise Exception("Application not found")

            app_row = app_resp.data[0]

            cand_resp = client.table("candidates").select("*").eq("id", app_row["candidate_id"]).execute()
            candidate = cand_resp.data[0] if cand_resp.data else {}

            job_resp = client.table("job_postings").select("*").eq("id", app_row["job_posting_id"]).execute()
            job = job_resp.data[0] if job_resp.data else {}

            # 2. Historial de mensajes (lo adaptamos a roles)
            msgs_resp = client.table("interview_messages")\
                .select("*")\
                .eq("application_id", application_id)\
                .order("order_index")\
                .execute()

            conversation_history = []
            for msg in msgs_resp.data or []:
                role = msg["sender"]  # "agent" | "candidate"

                cat = msg.get("question_category") or "knockout"
                if cat not in ("knockout", "technical", "soft_skills", "closing"):
                    cat = "knockout"

                idx = msg.get("order_index") or 0
                if idx < 0:
                    idx = 0

                conversation_history.append({
                    "role": role,
                    "content": msg["message_text"],
                    "timestamp": msg.get("timestamp") or datetime.utcnow().isoformat(),
                    "category": cat,
                    "order_index": idx,
                })


            # 3. Construir interview_state compatible con LangGraph
            interview_state = {
                "job_posting_id": app_row["job_posting_id"],
                "candidate_id": app_row["candidate_id"],
                "current_phase": app_row.get("current_phase", "knockout"),
                "completed_phases": app_row.get("completed_phases", []),
                "conversation_history": conversation_history,
                "knockout_scores": app_row.get("knockout_scores", []),
                "technical_scores": app_row.get("technical_scores", []),
                "soft_skills_scores": app_row.get("soft_skills_scores", []),
                # Opcional: contador de fases
                "phase_counter": app_row.get("phase_counter"),
            }

            MAX_CV_CONTEXT = 1000  # o el número que quieras


            if job.get("description"):
                conversation_history.insert(0, {
                    "role": "agent",
                    "content": f"Contexto del puesto: {job.get('title','')}\n{job['description']}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": "knockout",  # usar una categoría válida
                    "order_index": 0,
                })

            if candidate.get("cv_text_extracted"):
                conversation_history.insert(1, {
                    "role": "agent",
                    "content": f"Contexto del CV del candidato:\n{candidate['cv_text_extracted'][:MAX_CV_CONTEXT]}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": "knockout",  # también knockout para el contexto inicial
                    "order_index": 1,
                })

            payload = {
                "application_id": application_id,
                "candidate_message": candidate_message,
                "interview_state": interview_state,
            }

            async with httpx.AsyncClient(timeout=30.0) as http_client:
                url = f"{settings.LANGGRAPH_URL}/interview-step"
                print("DEBUG LangGraph URL:", url)
                print("DEBUG LangGraph payload sample:", {
                    "application_id": payload["application_id"],
                    "candidate_message": payload["candidate_message"],
                    "interview_state_keys": list(payload["interview_state"].keys()),
                })

                response = await http_client.post(url, json=payload)
                print("DEBUG LangGraph status:", response.status_code)
                print("DEBUG LangGraph body:", response.text[:400])

                if response.status_code == 200:
                    return response.json()
                else:
                    print("DEBUG non-200 from LangGraph, using fallback")
                    return {
                        "should_continue": True,
                        "next_question": "Gracias por tu respuesta. ¿Puedes contarme más sobre tu experiencia?",
                        "phase": "technical",
                        "score": None,
                    }

        except Exception as e:
            print("Error calling LangGraph:", str(e))
            return {
                "should_continue": True,
                "next_question": "Gracias. ¿Puedes elaborar más sobre eso?",
                "phase": "technical",
                "score": None,
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
        print("===== WebSocket exception =====")
        traceback.print_exc()
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
