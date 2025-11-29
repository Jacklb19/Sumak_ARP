from app.core.supabase_client import SupabaseClient
from app.services.llm_service import LLMService
from typing import Dict, Any, Optional
from fastapi import HTTPException, status


class ScoringService:
    """Servicio para calcular scores de candidatos"""

    def __init__(self):
        self.llm_service = LLMService()

    async def calculate_cv_score(
        self,
        candidate_id: str,
        job_posting_id: str
    ) -> Dict[str, Any]:
        """
        Calcular score del CV
        
        Según PARTE 3.2 del MD - Endpoint POST /scoring/calculate-cv-score:
        1. Recuperar CV text + embedding
        2. Recuperar job requirements
        3. Llamar a LLM para análisis
        4. Guardar en applications.cv_score
        5. Retornar score + explicación
        """
        client = SupabaseClient.get_client()
        
        # 1. Recuperar candidato
        try:
            response = client.table("candidates").select(
                "cv_text_extracted, cv_embedding"
            ).eq("id", candidate_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Candidate not found"
                )
            
            candidate = response.data[0]
            cv_text = candidate.get("cv_text_extracted", "")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving candidate: {str(e)}"
            )
        
        # 2. Recuperar vacante
        try:
            response = client.table("job_postings").select(
                "title, description, required_skills, nice_to_have_skills"
            ).eq("id", job_posting_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job posting not found"
                )
            
            job = response.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving job posting: {str(e)}"
            )
        
        # 3. Llamar a LLM para análisis
        try:
            score_data = await self.llm_service.analyze_cv_vs_job(
                cv_text=cv_text,
                job_title=job["title"],
                job_description=job["description"],
                required_skills=job.get("required_skills"),
                nice_to_have_skills=job.get("nice_to_have_skills")
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing CV: {str(e)}"
            )
        
        return score_data

    async def calculate_global_score(
        self,
        application_id: str,
        job_posting_id: str,
        cv_score: float,
        technical_score: float,
        soft_skills_score: float,
        scoring_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calcular score global
        
        Según PARTE 3.2 del MD - Endpoint POST /scoring/calculate-global-score:
        Fórmula: global = (cv * 0.4) + (technical * 0.4) + (soft_skills * 0.2)
        """
        
        # Usar pesos por defecto si no se proporcionan
        if scoring_weights is None:
            scoring_weights = {
                "cv": 0.4,
                "technical": 0.4,
                "soft_skills": 0.2
            }
        
        # Calcular score global
        global_score = (
            cv_score * scoring_weights.get("cv", 0.4) +
            technical_score * scoring_weights.get("technical", 0.4) +
            soft_skills_score * scoring_weights.get("soft_skills", 0.2)
        )
        
        # Redondear a 1 decimal
        global_score = round(global_score, 1)
        
        # Generar explicación
        explanation = (
            f"Score global calculado como promedio ponderado: "
            f"{scoring_weights.get('cv', 0.4)*100:.0f}% CV ({cv_score}) + "
            f"{scoring_weights.get('technical', 0.4)*100:.0f}% técnica ({technical_score}) + "
            f"{scoring_weights.get('soft_skills', 0.2)*100:.0f}% soft skills ({soft_skills_score})."
        )
        
        # Actualizar en BD
        try:
            client = SupabaseClient.get_client()
            client.table("applications").update({
                "global_score": global_score,
                "global_score_explanation": explanation
            }).eq("id", application_id).execute()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving global score: {str(e)}"
            )
        
        return {
            "global_score": global_score,
            "explanation": explanation
        }

    async def update_application_scores(
        self,
        application_id: str,
        cv_score: Optional[float] = None,
        technical_score: Optional[float] = None,
        soft_skills_score: Optional[float] = None,
        explanations: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Actualizar todos los scores de una aplicación
        """
        client = SupabaseClient.get_client()
        
        update_data = {}
        if cv_score is not None:
            update_data["cv_score"] = cv_score
            if explanations and "cv" in explanations:
                update_data["cv_score_explanation"] = explanations["cv"]
        
        if technical_score is not None:
            update_data["technical_score"] = technical_score
            if explanations and "technical" in explanations:
                update_data["technical_score_explanation"] = explanations["technical"]
        
        if soft_skills_score is not None:
            update_data["soft_skills_score"] = soft_skills_score
            if explanations and "soft_skills" in explanations:
                update_data["soft_skills_score_explanation"] = explanations["soft_skills"]
        
        try:
            response = client.table("applications").update(update_data).eq(
                "id", application_id
            ).execute()
            
            return {"success": True, "updated": len(response.data) > 0}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating scores: {str(e)}"
            )