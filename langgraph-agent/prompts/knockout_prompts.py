"""Prompts for knockout phase."""

from typing import Dict, List


def get_knockout_question_prompt(
    job_title: str,
    knockout_criteria: Dict,
    cv_text: str,
    previous_questions: List[str]
) -> str:
    """
    Generate prompt for knockout question.
    
    Args:
        job_title: Title of the job
        knockout_criteria: Knockout criteria from job posting
        cv_text: Candidate CV text
        previous_questions: Questions already asked
        
    Returns:
        Formatted prompt
    """
    previous_q_text = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "Ninguna"
    
    return f"""Eres un entrevistador de recursos humanos especializado en evaluar requisitos mínimos obligatorios.

**Contexto de la vacante:**
- Puesto: {job_title}
- Criterios knockout (requisitos mínimos obligatorios):
{_format_knockout_criteria(knockout_criteria)}

**CV del candidato (extracto):**
{cv_text[:500]}

**Preguntas knockout ya realizadas:**
{previous_q_text}

**Tu tarea:**
Genera UNA pregunta de knockout que evalúe un requisito mínimo DIFERENTE a los ya preguntados.

**Características de la pregunta:**
1. Debe ser directa y cerrada (Sí/No o valor numérico específico)
2. Debe evaluar un requisito crítico del puesto
3. La respuesta debe ser verificable objetivamente
4. Evita preguntas redundantes o similares a las ya hechas
5. Máximo 150 caracteres

**Formato de salida:**
QUESTION: [Tu pregunta aquí]
EXPECTED_FORMAT: [yes/no | numeric | specific_value]
CRITICAL_REQUIREMENT: [Qué requisito evalúa]

**Ejemplo:**
QUESTION: ¿Tienes al menos 3 años de experiencia con Python en producción?
EXPECTED_FORMAT: yes/no
CRITICAL_REQUIREMENT: Años de experiencia con Python
"""


def get_knockout_evaluation_prompt(
    question: str,
    candidate_answer: str,
    knockout_criteria: Dict,
    job_title: str
) -> str:
    """
    Generate prompt for knockout answer evaluation.
    
    Args:
        question: The knockout question asked
        candidate_answer: Candidate's answer
        knockout_criteria: Knockout criteria from job posting
        job_title: Title of the job
        
    Returns:
        Formatted evaluation prompt
    """
    return f"""Eres un evaluador experto de requisitos mínimos para el puesto de {job_title}.

**Criterios knockout del puesto:**
{_format_knockout_criteria(knockout_criteria)}

**Pregunta realizada:**
{question}

**Respuesta del candidato:**
{candidate_answer}

**Tu tarea:**
Evalúa si el candidato CUMPLE o NO CUMPLE el requisito mínimo.

**Criterios de evaluación:**
1. Si la respuesta es clara y cumple el requisito → SCORE: 5.0, AUTO_REJECT: false
2. Si la respuesta es ambigua pero probable que cumpla → SCORE: 3.5, AUTO_REJECT: false
3. Si NO cumple el requisito mínimo → SCORE: 1.0, AUTO_REJECT: true
4. Si la respuesta es evasiva o no responde → SCORE: 1.5, AUTO_REJECT: true

**Formato de salida:**
PASS: [yes/no]
SCORE: [1.0-5.0]
EXPLANATION: [Razón corta en máximo 100 caracteres]
AUTO_REJECT: [true/false]

**Ejemplos:**

Ejemplo 1 (Cumple):
PASS: yes
SCORE: 5.0
EXPLANATION: Tiene 5 años de experiencia, cumple el mínimo de 3 años
AUTO_REJECT: false

Ejemplo 2 (No cumple):
PASS: no
SCORE: 1.0
EXPLANATION: Solo tiene 1 año de experiencia, no cumple mínimo de 3
AUTO_REJECT: true

Ejemplo 3 (Ambiguo):
PASS: no
SCORE: 1.5
EXPLANATION: Respuesta evasiva, no confirma años de experiencia
AUTO_REJECT: true
"""


def _format_knockout_criteria(criteria: Dict) -> str:
    """Format knockout criteria for prompt."""
    if not criteria:
        return "No se especificaron criterios knockout explícitos."
    
    formatted_lines = []
    
    if "min_years_experience" in criteria:
        formatted_lines.append(f"- Mínimo {criteria['min_years_experience']} años de experiencia")
    
    if "required_languages" in criteria:
        langs = ", ".join(criteria["required_languages"])
        formatted_lines.append(f"- Lenguajes obligatorios: {langs}")
    
    if "required_education" in criteria:
        formatted_lines.append(f"- Formación mínima: {criteria['required_education']}")
    
    if "salary_expectation_max" in criteria:
        formatted_lines.append(f"- Expectativa salarial máxima: ${criteria['salary_expectation_max']:,}")
    
    if "work_authorization" in criteria:
        formatted_lines.append(f"- Autorización de trabajo: {criteria['work_authorization']}")
    
    # Add any other criteria
    for key, value in criteria.items():
        if key not in ["min_years_experience", "required_languages", "required_education", 
                       "salary_expectation_max", "work_authorization"]:
            formatted_lines.append(f"- {key}: {value}")
    
    return "\n".join(formatted_lines) if formatted_lines else "Criterios generales del puesto"
