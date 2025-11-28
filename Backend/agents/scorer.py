import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from schemas.state import AgentState, EvaluationStatus
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.2)

def score_candidate_node(state: AgentState) -> dict:
    """
    Node that calculates final scores
    
    Input: cv_score, questions_asked, job_requirements
    Output: technical_score, behavioral_score, overall_score, recommendation
    """
    
    prompt = ChatPromptTemplate.from_template("""
    SENIOR EVALUATOR: Calculate final scores for the candidate

    DATA:
    - CV Score: {cv_score}
    - Technical Questions: {num_tech_questions}
    - Behavioral Questions: {num_behavioral_questions}
    - Position: {job_requirements}

    SCORING FORMULA:
    - Technical Score: 0-100 (based on CV + tech questions)
    - Behavioral Score: 0-100 (based on behavioral questions)
    - Overall Score: (CV*0.2) + (Technical*0.4) + (Behavioral*0.4)
    - Recommendation: hire (>=75) / maybe (50-75) / reject (<50)

    RESPOND IN JSON:
    {{
      "technical_score": 0-100,
      "behavioral_score": 0-100,
      "recommendation": "hire/maybe/reject"
    }}
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "cv_score": state.cv_score or 0,
            "num_tech_questions": len(state.questions_asked) // 2,
            "num_behavioral_questions": len(state.questions_asked) // 3,
            "job_requirements": ", ".join(state.job_requirements)
        })
        
        # Clean response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
            content = content.rstrip("```").strip()
        
        result = json.loads(content)
        
        technical = float(result.get("technical_score", 60))
        behavioral = float(result.get("behavioral_score", 60))
        
        # Formula: (CV*0.2) + (Technical*0.4) + (Behavioral*0.4)
        overall = (
            (state.cv_score or 0) * 0.2 +
            technical * 0.4 +
            behavioral * 0.4
        )
        
        logger.info(f"Scores - Technical: {technical}, Behavioral: {behavioral}, Overall: {overall}")
        
        return {
            "technical_score": technical,
            "behavioral_score": behavioral,
            "overall_score": round(overall, 2),
            "recommendation": result.get("recommendation", "reject"),
            "status": EvaluationStatus.COMPLETED
        }
    
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        return {
            "technical_score": 60,
            "behavioral_score": 60,
            "overall_score": 60,
            "recommendation": "reject",
            "status": EvaluationStatus.FAILED,
            "errors": state.errors + [f"Scoring error: {str(e)}"]
        }
