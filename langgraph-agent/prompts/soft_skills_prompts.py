"""Prompts for soft skills phase."""

from typing import Dict, List


def get_soft_skills_question_prompt(
    job_title: str,
    job_description: str,
    previous_questions: List[str]
) -> str:
    """
    Generate prompt for soft skills question.
    
    Args:
        job_title: Title of the job
        job_description: Job description
        previous_questions: Questions already asked
        
    Returns:
        Formatted prompt
    """
    previous_q_text = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "Ninguna"
    
    return f"""Eres un psicólogo organizacional especializado en evaluación de competencias blandas.

**Puesto:**
{job_title}

**Descripción del puesto:**
{job_description[:500]}

**Preguntas de soft skills ya realizadas:**
{previous_q_text}

**Competencias clave a evaluar:**
1. Trabajo en equipo y colaboración
2. Comunicación efectiva
3. Resolución de conflictos
4. Manejo de estrés y presión
5. Adaptabilidad al cambio
6. Liderazgo (si aplica)
7. Iniciativa y proactividad

**Tu tarea:**
Genera UNA pregunta conductual/situacional que evalúe una competencia DIFERENTE a las ya preguntadas.

**Técnica STAR recomendada:**
- Situación: Contexto
- Tarea: Qué debía hacer
- Acción: Qué hizo específicamente
- Resultado: Qué pasó

**Características de la pregunta:**
- Debe ser abierta (no Sí/No)
- Debe pedir ejemplos concretos de experiencia pasada
- Debe iniciar con "Cuéntame de una vez que..." o "Cómo manejarías si..."
- Máximo 150 caracteres
- Evita preguntas genéricas o hipotéticas sin contexto

**Formato de salida:**
QUESTION: [Tu pregunta aquí]
COMPETENCY_ASSESSED: [Competencia específica que evalúa]
RED_FLAGS_TO_WATCH: [1-2 señales de alerta a detectar en la respuesta]

**Ejemplos:**

Ejemplo 1 (Trabajo en equipo):
QUESTION: Cuéntame de una vez que tuviste un desacuerdo técnico con un compañero. ¿Cómo lo resolvieron?
COMPETENCY_ASSESSED: Resolución de conflictos
RED_FLAGS_TO_WATCH: Culpar a otros, no asumir responsabilidad

Ejemplo 2 (Manejo de estrés):
QUESTION: Describe una situación donde tuviste múltiples deadlines al mismo tiempo. ¿Cómo priorizaste?
COMPETENCY_ASSESSED: Manejo de presión y organización
RED_FLAGS_TO_WATCH: No tener estrategia clara, no delegar

Ejemplo 3 (Comunicación):
QUESTION: ¿Cómo explicarías un concepto técnico complejo a alguien sin background técnico?
COMPETENCY_ASSESSED: Comunicación adaptativa
RED_FLAGS_TO_WATCH: Usar jerga técnica, falta de empatía con audiencia
"""


def get_soft_skills_evaluation_prompt(
    question: str,
    candidate_answer: str,
    competency: str,
    red_flags: List[str]
) -> str:
    """
    Generate prompt for soft skills answer evaluation.
    
    Args:
        question: The soft skills question asked
        candidate_answer: Candidate's answer
        competency: Competency being assessed
        red_flags: Red flags to watch for
        
    Returns:
        Formatted evaluation prompt
    """
    return f"""Eres un psicólogo organizacional experto en evaluación de competencias blandas.

**Competencia evaluada:**
{competency}

**Pregunta realizada:**
{question}

**Respuesta del candidato:**
{candidate_answer}

**Red flags a detectar:**
{', '.join(red_flags)}

**Criterios de evaluación:**

**5.0 - Excelente:**
- Respuesta estructurada con ejemplo concreto (STAR completo)
- Demuestra autorreflexión y aprendizaje
- Muestra actitud proactiva y responsabilidad
- Sin red flags detectados

**4.0 - Buena:**
- Respuesta con ejemplo concreto pero menos estructurado
- Demuestra competencia sólida
- Actitud positiva
- Sin red flags significativos

**3.0 - Aceptable:**
- Respuesta genérica o poco específica
- Competencia presente pero no destacada
- Ejemplo poco detallado
- Algún red flag menor

**2.0 - Débil:**
- Respuesta vaga o evasiva
- No proporciona ejemplos concretos
- Presencia de red flags
- Falta de autorreflexión

**1.0 - Insuficiente:**
- No responde la pregunta
- Múltiples red flags (culpar a otros, actitud negativa, etc.)
- Demuestra falta de la competencia

**Formato de salida:**
SCORE: [1.0-5.0]
EXPLANATION: [Análisis específico en máximo 150 caracteres]
COMPETENCY: [{competency}]
RED_FLAGS_DETECTED: [Lista de red flags encontrados, o "Ninguno"]
POSITIVE_INDICATORS: [Aspectos positivos destacables, o "Pocos"]

**Ejemplo:**
SCORE: 4.5
EXPLANATION: Ejemplo concreto bien estructurado. Demuestra capacidad de resolver conflictos constructivamente
COMPETENCY: Resolución de conflictos
RED_FLAGS_DETECTED: Ninguno
POSITIVE_INDICATORS: Asumió responsabilidad, buscó win-win, comunicación abierta
"""
