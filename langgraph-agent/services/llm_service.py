"""LLM service for question generation and evaluation (GOOGLE GEMINI)."""

from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
from utils.logger import get_logger
from utils.parsers import extract_question_from_llm, parse_evaluation_response

logger = get_logger(__name__)


class LLMService:
    """Singleton LLM service using Google Gemini."""
    
    _instance: ChatGoogleGenerativeAI = None
    
    @classmethod
    def get_llm(cls) -> ChatGoogleGenerativeAI:
        """Get or create LLM instance."""
        if cls._instance is None:
            cls._instance = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
                google_api_key=settings.google_api_key
            )
            logger.info("llm_service_initialized", model=settings.gemini_model)
        return cls._instance


def generate_question(prompt: str) -> str:
    """
    Generate question using LLM.
    
    Args:
        prompt: Prompt for question generation
        
    Returns:
        Generated question text
    """
    llm = LLMService.get_llm()
    
    try:
        response = llm.invoke(prompt)
        question = extract_question_from_llm(response.content)
        
        logger.info(
            "question_generated",
            prompt_length=len(prompt),
            question_length=len(question)
        )
        
        return question
    
    except Exception as e:
        logger.error("question_generation_failed", error=str(e))
        raise


def evaluate_answer(prompt: str) -> Dict:
    """
    Evaluate candidate answer using LLM.
    
    Args:
        prompt: Evaluation prompt
        
    Returns:
        Dict with score, explanation, and other metrics
    """
    llm = LLMService.get_llm()
    
    try:
        response = llm.invoke(prompt)
        evaluation = parse_evaluation_response(response.content)
        
        logger.info(
            "answer_evaluated",
            score=evaluation.get("score"),
            auto_reject=evaluation.get("auto_reject", False)
        )
        
        return evaluation
    
    except Exception as e:
        logger.error("answer_evaluation_failed", error=str(e))
        raise


def calculate_cv_score(cv_text: str, job_requirements: Dict) -> Dict:
    """
    Calculate CV score based on job requirements.
    
    Args:
        cv_text: Extracted CV text
        job_requirements: Job requirements dict
        
    Returns:
        Dict with score and explanation
    """
    llm = LLMService.get_llm()
    
    prompt = f"""Analiza el CV del candidato contra los requisitos del puesto.

CV del candidato (primeros 1000 caracteres):
{cv_text[:1000]}

Requisitos del puesto:
- Skills requeridos: {job_requirements.get('required_skills', {})}
- Skills deseables: {job_requirements.get('nice_to_have_skills', {})}

Evalúa y devuelve:
SCORE: [0-100]
EXPLANATION: [Explicación corta de máximo 200 caracteres]

Considera:
1. Coincidencia de skills técnicos
2. Años de experiencia
3. Formación académica relevante
4. Logros destacables
"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Parse score
        import re
        score_match = re.search(r"SCORE:\s*(\d+)", content)
        score = int(score_match.group(1)) if score_match else 70
        
        # Parse explanation
        explanation_match = re.search(r"EXPLANATION:\s*(.+?)(?:\n|$)", content, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else "Evaluación completada"
        
        logger.info("cv_score_calculated", score=score)
        
        return {
            "score": score,
            "explanation": explanation
        }
    
    except Exception as e:
        logger.error("cv_score_calculation_failed", error=str(e))
        return {
            "score": 70,
            "explanation": "Error al calcular score del CV"
        }
