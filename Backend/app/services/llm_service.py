from groq import Groq
from app.core.config import settings
from typing import Dict, Any, Optional
import json


class LLMService:
    """Servicio para llamadas a Groq + Llama"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-specdec"  # Modelo recomendado

    async def analyze_cv_vs_job(
        self,
        cv_text: str,
        job_title: str,
        job_description: str,
        required_skills: Optional[Dict[str, Any]] = None,
        nice_to_have_skills: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analizar CV vs requisitos del puesto
        
        Retorna:
        - score: 0-100
        - sub_scores: {educacion, experiencia_stack, logros, continuidad_empleo}
        - explanation: string
        """
        
        prompt = f"""
Eres un experto en reclutamiento y análisis de CVs. Analiza el siguiente CV contra los requisitos del puesto.

PUESTO: {job_title}
DESCRIPCIÓN: {job_description}

REQUISITOS CLAVE:
{json.dumps(required_skills, ensure_ascii=False) if required_skills else "No especificados"}

NICE TO HAVE:
{json.dumps(nice_to_have_skills, ensure_ascii=False) if nice_to_have_skills else "Ninguno"}

CV DEL CANDIDATO:
{cv_text[:2000]}

Proporciona un análisis estructurado en JSON con:
- score: número 0-100
- sub_scores: objeto con educacion, experiencia_stack, logros, continuidad_empleo (0-100 cada uno)
- explanation: explicación corta (máximo 200 palabras)

Responde SOLO en JSON, sin markdown.
"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en RH. Responde en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = message.choices[0].message.content
            
            # Parsear JSON
            result = json.loads(response_text)
            
            return {
                "score": result.get("score", 0),
                "sub_scores": result.get("sub_scores", {}),
                "explanation": result.get("explanation", "")
            }
            
        except json.JSONDecodeError:
            # Si la respuesta no es JSON válido, retornar default
            return {
                "score": 50,
                "sub_scores": {},
                "explanation": "Error parsing response"
            }
        except Exception as e:
            raise Exception(f"Error calling Groq: {str(e)}")

    async def generate_job_context(
        self,
        job_title: str,
        job_description: str,
        required_skills: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generar contexto de la vacante para el agente entrevistador
        
        Usado en POST /job-postings para generar job_template_context
        """
        
        prompt = f"""
Eres un coordinador de entrevistas. Genera un contexto BREVE pero detallado para una entrevista de este puesto.

PUESTO: {job_title}
DESCRIPCIÓN: {job_description[:500]}
REQUISITOS: {json.dumps(required_skills, ensure_ascii=False) if required_skills else "No especificados"}

Proporciona:
- 2-3 preguntas knockout (eliminatorias)
- 3-4 temas técnicos a explorar
- 2-3 áreas de soft skills a evaluar

Formato claro y conciso (máximo 300 palabras).
"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return message.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating context: {str(e)}")

    async def analyze_candidates_for_recruiter(
        self,
        job_title: str,
        candidates_data: list,
        question: str
    ) -> str:
        """
        Analizar candidatos para chat con reclutador
        
        Usado en POST /agent-chat
        """
        
        candidates_summary = "\n".join([
            f"- {c['name']} (Score: {c['score']}): {c['summary']}"
            for c in candidates_data
        ])
        
        prompt = f"""
Eres un asistente de RH experto. Analiza estos candidatos y responde la pregunta del reclutador.

PUESTO: {job_title}

CANDIDATOS:
{candidates_summary}

PREGUNTA DEL RECLUTADOR:
{question}

Proporciona un análisis detallado, citando candidatos específicos con datos concretos.
"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return message.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error analyzing candidates: {str(e)}")

    async def generate_onboarding_email(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
        start_date: str,
        first_day_checklist: Optional[list] = None,
        goals_30_60_90: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generar email de onboarding personalizado
        
        Usado en POST /onboarding/generate
        
        Retorna:
        - subject: asunto
        - body: cuerpo del email
        """
        
        checklist_str = "\n".join([f"- {item}" for item in first_day_checklist]) if first_day_checklist else ""
        goals_str = json.dumps(goals_30_60_90, ensure_ascii=False) if goals_30_60_90 else ""
        
        prompt = f"""
Genera un email de bienvenida cálido pero profesional para un nuevo empleado.

DATOS:
- Nombre: {candidate_name}
- Puesto: {job_title}
- Empresa: {company_name}
- Primer día: {start_date}

CHECKLIST PRIMER DÍA:
{checklist_str}

OBJETIVOS 30/60/90:
{goals_str}

El email debe:
- Ser cálido y acogedor
- Incluir pasos concretos del primer día
- Mencionar contactos clave
- Ser profesional pero ameno
- Máximo 300 palabras

Responde en JSON con: {{"subject": "...", "body": "..."}}
"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            response_text = message.choices[0].message.content
            result = json.loads(response_text)
            
            return {
                "subject": result.get("subject", "Welcome to our team!"),
                "body": result.get("body", "")
            }
            
        except json.JSONDecodeError:
            return {
                "subject": f"Welcome to {company_name}, {candidate_name}!",
                "body": f"Bienvenido al equipo. Tu primer día es {start_date}."
            }
        except Exception as e:
            raise Exception(f"Error generating onboarding email: {str(e)}")