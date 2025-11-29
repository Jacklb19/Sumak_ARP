"""LLM service for question generation and evaluation (Multi-provider)."""

from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from config.settings import settings
from utils.logger import get_logger
from utils.parsers import extract_question_from_llm, parse_evaluation_response

logger = get_logger(__name__)

class LLMService:
    """Multi-provider LLM service."""
    
    _instance = None
    
    @classmethod
    def get_llm(cls):
        """Get LLM instance based on provider."""
        if cls._instance is None:
            if settings.llm_provider == "groq":
                cls._instance = ChatGroq(
                    model=settings.groq_model,
                    api_key=settings.groq_api_key,
                    temperature=settings.groq_temperature,
                )
                logger.info("groq_llm_initialized", model=settings.groq_model)
            else:  # gemini
                cls._instance = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    temperature=settings.gemini_temperature,
                    max_output_tokens=settings.gemini_max_tokens,
                    google_api_key=settings.google_api_key
                )
                logger.info("gemini_llm_initialized", model=settings.gemini_model)
        return cls._instance

# Las funciones generate_question, evaluate_answer, calculate_cv_score quedan IGUALES
def generate_question(prompt: str) -> str:
    llm = LLMService.get_llm()
    try:
        response = llm.invoke(prompt)
        question = extract_question_from_llm(response.content)
        logger.info(
            "question_generated",
            provider=settings.llm_provider,
            prompt_length=len(prompt),
            question_length=len(question)
        )
        return question
    except Exception as e:
        logger.error("question_generation_failed", error=str(e))
        raise

def evaluate_answer(prompt: str) -> Dict:
    llm = LLMService.get_llm()
    try:
        response = llm.invoke(prompt)
        evaluation = parse_evaluation_response(response.content)
        logger.info(
            "answer_evaluated",
            provider=settings.llm_provider,
            score=evaluation.get("score"),
            auto_reject=evaluation.get("auto_reject", False)
        )
        return evaluation
    except Exception as e:
        logger.error("answer_evaluation_failed", error=str(e))
        raise

def calculate_cv_score(cv_text: str, job_requirements: Dict) -> Dict:
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
        
        import re
        score_match = re.search(r"SCORE:\s*(\d+)", content)
        score = int(score_match.group(1)) if score_match else 70
        
        explanation_match = re.search(r"EXPLANATION:\s*(.+?)(?:\n|$)", content, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else "Evaluación completada"
        
        logger.info("cv_score_calculated", provider=settings.llm_provider, score=score)
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
