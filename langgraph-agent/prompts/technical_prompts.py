"""Prompts for technical phase."""

from typing import Dict, List


def get_technical_question_prompt(
    job_title: str,
    required_skills: Dict,
    cv_text: str,
    seniority: str,
    previous_questions: List[str],
    previous_scores: List[Dict]
) -> str:
    """
    Generate prompt for adaptive technical question.
    
    Args:
        job_title: Title of the job
        required_skills: Required technical skills
        cv_text: Candidate CV text
        seniority: Candidate seniority level
        previous_questions: Questions already asked
        previous_scores: Scores from previous answers
        
    Returns:
        Formatted prompt
    """
    # Analyze performance
    performance_context = _analyze_previous_performance(previous_scores)
    
    previous_q_text = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "Ninguna"
    
    return f"""Eres un entrevistador técnico experto para el puesto de {job_title}.

**Stack técnico requerido:**
{_format_required_skills(required_skills)}

**Nivel esperado del candidato:**
{seniority.upper()} (ajusta la dificultad de la pregunta a este nivel)

**CV del candidato (extracto relevante):**
{cv_text[:800]}

**Preguntas técnicas ya realizadas:**
{previous_q_text}

**Rendimiento previo del candidato:**
{performance_context}

**Tu tarea:**
Genera UNA pregunta técnica adaptativa que:

1. **Si el candidato está respondiendo bien (últimos scores ≥ 4.0):**
   - Profundiza en el mismo tema con más detalle
   - Aumenta la complejidad (casos edge, optimización, arquitectura)
   
2. **Si el candidato está respondiendo débil (últimos scores ≤ 2.5):**
   - Cambia a otro skill del stack requerido
   - Reduce la complejidad para evaluar conocimientos básicos
   
3. **Si no hay historial o rendimiento medio:**
   - Pregunta sobre un skill clave del stack aún no evaluado
   - Dificultad media para el nivel {seniority}

**Características de la pregunta:**
- Debe ser práctica, no teórica abstracta
- Respondible en 2-3 líneas (no ensayos)
- Relacionada con casos reales de trabajo
- Máximo 200 caracteres
- Evita preguntas de "definición", prefiere "cómo harías X"

**Formato de salida:**
QUESTION: [Tu pregunta aquí]
DIFFICULTY: [easy/medium/hard]
SKILL_EVALUATED: [Skill específico que evalúa]
EXPECTED_KEYWORDS: [2-3 keywords que esperas en una buena respuesta]

**Ejemplo para Senior Python Developer:**
QUESTION: ¿Cómo optimizarías una consulta SQL que está causando timeout en producción con 10M de registros?
DIFFICULTY: hard
SKILL_EVALUATED: SQL optimization
EXPECTED_KEYWORDS: indexes, query plan, partitioning
"""


def get_technical_evaluation_prompt(
    question: str,
    candidate_answer: str,
    expected_keywords: List[str],
    required_skills: Dict,
    seniority: str
) -> str:
    """
    Generate prompt for technical answer evaluation.
    
    Args:
        question: The technical question asked
        candidate_answer: Candidate's answer
        expected_keywords: Expected keywords in answer
        required_skills: Required technical skills
        seniority: Expected seniority level
        
    Returns:
        Formatted evaluation prompt
    """
    return f"""Eres un evaluador técnico experto. Evalúa la respuesta del candidato para nivel {seniority.upper()}.

**Pregunta técnica:**
{question}

**Respuesta del candidato:**
{candidate_answer}

**Keywords esperados:**
{', '.join(expected_keywords)}

**Stack técnico del puesto:**
{_format_required_skills(required_skills)}

**Criterios de evaluación (ajustados al nivel {seniority}):**

**5.0 - Excelente:**
- Respuesta completa y precisa
- Menciona mejores prácticas
- Demuestra experiencia práctica
- Usa terminología correcta

**4.0 - Buena:**
- Respuesta correcta en lo fundamental
- Falta algún detalle o profundidad
- Demuestra conocimiento sólido

**3.0 - Aceptable:**
- Respuesta parcialmente correcta
- Conceptos básicos entendidos
- Le falta práctica o profundidad

**2.0 - Débil:**
- Respuesta imprecisa o incompleta
- Confusión en conceptos
- Conocimiento superficial

**1.0 - Insuficiente:**
- Respuesta incorrecta o fuera de contexto
- No demuestra conocimiento del tema

**Formato de salida:**
SCORE: [1.0-5.0]
EXPLANATION: [Razón específica en máximo 150 caracteres, menciona qué falta o qué está bien]
DIFFICULTY: [easy/medium/hard según cómo respondió]
FOLLOW_UP_SUGGESTION: [Si score ≥ 4.0, sugiere tema para profundizar; si ≤ 2.5, sugiere cambiar de tema]

**Ejemplo:**
SCORE: 4.5
EXPLANATION: Excelente, mencionó indexes y partitioning. Faltó query plan analysis
DIFFICULTY: hard
FOLLOW_UP_SUGGESTION: Profundizar en database sharding strategies
"""


def _format_required_skills(skills: Dict) -> str:
    """Format required skills for prompt."""
    if not skills:
        return "No se especificaron skills técnicos."
    
    formatted_lines = []
    
    if "languages" in skills:
        langs = ", ".join(skills["languages"])
        formatted_lines.append(f"- Lenguajes: {langs}")
    
    if "frameworks" in skills:
        frameworks = ", ".join(skills["frameworks"])
        formatted_lines.append(f"- Frameworks: {frameworks}")
    
    if "databases" in skills:
        dbs = ", ".join(skills["databases"])
        formatted_lines.append(f"- Bases de datos: {dbs}")
    
    if "tools" in skills:
        tools = ", ".join(skills["tools"])
        formatted_lines.append(f"- Herramientas: {tools}")
    
    if "years_experience" in skills:
        formatted_lines.append(f"- Años de experiencia: {skills['years_experience']}")
    
    return "\n".join(formatted_lines) if formatted_lines else "Stack técnico general"


def _analyze_previous_performance(scores: List[Dict]) -> str:
    """Analyze previous performance to guide next question."""
    if not scores:
        return "No hay preguntas técnicas previas. Esta es la primera."
    
    recent_scores = [s["score"] for s in scores[-2:]]  # Last 2 scores
    avg_score = sum(recent_scores) / len(recent_scores)
    
    if avg_score >= 4.0:
        return f"El candidato está respondiendo MUY BIEN (promedio: {avg_score:.1f}/5). PROFUNDIZA en el último tema."
    elif avg_score >= 3.0:
        return f"El candidato está respondiendo ACEPTABLE (promedio: {avg_score:.1f}/5). Mantén nivel similar."
    else:
        return f"El candidato está respondiendo DÉBIL (promedio: {avg_score:.1f}/5). CAMBIA de tema o REDUCE complejidad."
