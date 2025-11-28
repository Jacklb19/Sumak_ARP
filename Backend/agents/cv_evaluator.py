import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from schemas.state import AgentState, EvaluationStatus
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)

def evaluate_cv_node(state: AgentState) -> dict:
    """
    Node that evaluates the CV and returns initial score
    
    Input: cv_text, job_requirements, job_description
    Output: cv_score, should_continue_technical, status
    """
    
    prompt = ChatPromptTemplate.from_template("""
    EXPERT RECRUITER: Evaluate this CV for the position

    CANDIDATE CV:
    {cv_text}

    POSITION REQUIRED:
    {job_requirements}

    JOB DESCRIPTION:
    {job_description}

    ANALYSIS:
    1. Score CV (0-100) based on match with requirements
    2. Skills detected
    3. Knowledge gaps
    4. Should continue to technical interview?

    RESPOND IN VALID JSON ONLY:
    {{
      "score": 0-100,
      "skills_found": ["skill1", "skill2"],
      "gaps": ["gap1"],
      "summary": "Brief analysis",
      "continue": true/false
    }}
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "cv_text": state.cv_text[:2000],  # Limit size
            "job_requirements": ", ".join(state.job_requirements),
            "job_description": state.job_description[:500]
        })
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
            content = content.rstrip("```").strip()
        
        result = json.loads(content)
        cv_score = float(result.get("score", 0))
        should_continue = result.get("continue", cv_score >= 50)
        
        logger.info(f"CV Score: {cv_score}, Continue: {should_continue}")
        
        return {
            "cv_score": cv_score,
            "should_continue_technical": should_continue,
            "status": EvaluationStatus.TECHNICAL_INTERVIEW if should_continue 
                     else EvaluationStatus.SCORING,
            "notes": f"CV Score: {cv_score}. Skills: {result.get('skills_found', [])}"
        }
    
    except Exception as e:
        logger.error(f"CV evaluation error: {e}")
        return {
            "cv_score": 0,
            "should_continue_technical": False,
            "status": EvaluationStatus.FAILED,
            "errors": state.errors + [f"CV evaluation error: {str(e)}"]
        }

def should_continue_to_interview(state: AgentState) -> bool:
    """
    Conditional router: decide if should continue to interview
    """
    return state.should_continue_technical
