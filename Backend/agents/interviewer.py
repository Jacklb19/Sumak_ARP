import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from schemas.state import AgentState, EvaluationStatus
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)

def ask_technical_question_node(state: AgentState) -> dict:
    """
    Node that generates technical interview questions
    
    Input: job_requirements, cv_score, previous_questions
    Output: questions_asked list
    """
    
    num_tech_questions = len([
        q for q in state.questions_asked 
        if "técnica" in q.lower() or "technical" in q.lower()
    ])
    
    # Stop if enough technical questions
    if num_tech_questions >= 3:
        return {"status": EvaluationStatus.BEHAVIORAL_INTERVIEW}
    
    prompt = ChatPromptTemplate.from_template("""
    TECHNICAL INTERVIEWER: Generate one technical question

    CONTEXT:
    - Position: {job_requirements}
    - CV Score: {cv_score}
    - Previous questions: {previous_questions}
    - Question #{question_number}

    Generate ONE NEW technical question appropriate for the level.
    
    RESPOND IN JSON:
    {{"question": "Your question here?"}}
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "job_requirements": ", ".join(state.job_requirements),
            "cv_score": state.cv_score or 0,
            "previous_questions": state.questions_asked[-2:] if state.questions_asked else [],
            "question_number": num_tech_questions + 1
        })
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
            content = content.rstrip("```").strip()
        
        result = json.loads(content)
        
        return {
            "questions_asked": state.questions_asked + [result.get("question", "Default question")]
        }
    
    except Exception as e:
        logger.error(f"Technical question error: {e}")
        return {
            "questions_asked": state.questions_asked + ["What is your experience with the main tech stack?"],
            "errors": state.errors + [str(e)]
        }

def ask_behavioral_question_node(state: AgentState) -> dict:
    """
    Node that generates behavioral interview questions
    
    Input: previous_questions
    Output: questions_asked list
    """
    
    num_behavioral = len([
        q for q in state.questions_asked 
        if "behavior" in q.lower() or "conflicto" in q.lower()
    ])
    
    # Stop if enough behavioral questions
    if num_behavioral >= 2:
        return {"status": EvaluationStatus.SCORING}
    
    prompt = ChatPromptTemplate.from_template("""
    BEHAVIORAL INTERVIEWER: Generate one behavioral question

    Generate ONE NEW behavioral question to assess soft skills and adaptability.
    
    RESPOND IN JSON:
    {{"question": "Your question here?"}}
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({})
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
            content = content.rstrip("```").strip()
        
        result = json.loads(content)
        
        return {
            "questions_asked": state.questions_asked + [result.get("question", "Default question")]
        }
    
    except Exception as e:
        logger.error(f"Behavioral question error: {e}")
        return {
            "questions_asked": state.questions_asked + ["Tell me about a challenge you overcame"],
            "errors": state.errors + [str(e)]
        }
