import os
import logging
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio


from schemas.state import AgentState
from agents.main_agent import create_recruitment_agent
from utils.supabase_client import SupabaseClient
from utils.llm_utils import validate_api_keys



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize clients
supabase_client = None
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global supabase_client, agent
    
    logger.info("🚀 Starting Sumak ARP Backend...")
    
    # Initialize Supabase
    try:
        supabase_client = SupabaseClient()
        logger.info("✅ Supabase connected")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
    
    # Initialize LangGraph Agent
    try:
        agent = create_recruitment_agent()
        logger.info("✅ LangGraph agent initialized")
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {e}")
    
    # Validate API keys
    validate_api_keys()
    
    yield
    
    logger.info("🛑 Shutting down Sumak ARP Backend")

# Create FastAPI app
app = FastAPI(
    title="Sumak ARP API",
    description="Agente de Reclutamiento Inteligente",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Sumak ARP",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check critical services
        supabase_status = "✓" if supabase_client else "✗"
        agent_status = "✓" if agent else "✗"
        openai_key = "✓" if os.getenv("OPENAI_API_KEY") else "✗"
        
        return {
            "status": "healthy",
            "services": {
                "supabase": supabase_status,
                "agent": agent_status,
                "openai": openai_key,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/evaluate")
async def evaluate_candidate(request: dict):
    """
    Evalúa un candidato completamente
    
    Request body:
    {
        "candidate_id": "str",
        "job_id": "str",
        "company_id": "str",
        "cv_text": "str",
        "job_requirements": ["skill1", "skill2"],
        "job_description": "str (opcional)"
    }
    """
    
    try:
        logger.info(f"📝 Evaluating candidate: {request.get('candidate_id')}")
        
        # Validate request
        required_fields = ["candidate_id", "job_id", "company_id", "cv_text"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Create agent state
        state = AgentState(
            candidate_id=request.get("candidate_id"),
            job_id=request.get("job_id"),
            company_id=request.get("company_id"),
            cv_text=request.get("cv_text", ""),
            job_requirements=request.get("job_requirements", []),
            job_description=request.get("job_description", "")
        )
        
        # Execute agent
        logger.info(f"🤖 Running agent for {state.candidate_id}")
        result = agent.invoke(state)
        
        # Save to Supabase (non-blocking)
        try:
            evaluation_data = {
                "candidate_id": result.candidate_id,
                "job_id": result.job_id,
                "company_id": result.company_id,
                "technical_score": float(result.technical_score or 0),
                "behavioral_score": float(result.behavioral_score or 0),
                "overall_score": float(result.overall_score or 0),
                "recommendation": result.recommendation,
                "interview_transcript": {
                    "questions": result.questions_asked,
                    "notes": result.notes
                }
            }
            
            supabase_client.create_evaluation(evaluation_data)
            supabase_client.update_candidate(
                result.candidate_id,
                {
                    "overall_score": result.overall_score,
                    "status": "completed"
                }
            )
            logger.info(f"✅ Evaluation saved to Supabase")
        except Exception as e:
            logger.warning(f"⚠️ Supabase save failed: {e}")
        
        # Return results
        return {
            "success": True,
            "candidate_id": result.candidate_id,
            "cv_score": round(result.cv_score or 0, 2),
            "technical_score": round(result.technical_score or 0, 2),
            "behavioral_score": round(result.behavioral_score or 0, 2),
            "overall_score": round(result.overall_score or 0, 2),
            "recommendation": result.recommendation,
            "status": result.status.value,
            "notes": result.notes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Evaluation error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "status": "failed"
        }

@app.post("/batch-evaluate")
async def batch_evaluate_candidates(requests: list):
    """
    Evalúa múltiples candidatos en batch
    """
    results = []
    
    for req in requests:
        result = await evaluate_candidate(req)
        results.append(result)
    
    return {
        "success": True,
        "total": len(requests),
        "completed": sum(1 for r in results if r.get("success")),
        "results": results
    }

@app.get("/evaluations/{company_id}")
async def get_evaluations(company_id: str, limit: int = 100):
    """
    Obtiene evaluaciones de una PYME
    """
    try:
        evaluations = supabase_client.get_evaluations_by_company(company_id, limit)
        return {
            "success": True,
            "company_id": company_id,
            "count": len(evaluations),
            "evaluations": evaluations
        }
    except Exception as e:
        logger.error(f"Error getting evaluations: {e}")
        return {"success": False, "error": str(e)}

@app.get("/stats/{company_id}")
async def get_company_stats(company_id: str):
    """
    Obtiene estadísticas de una PYME
    """
    try:
        stats = supabase_client.get_stats(company_id)
        return {
            "success": True,
            "company_id": company_id,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"success": False, "error": str(e)}

# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Error: {exc.detail}")
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc)
    }

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=os.getenv("ENVIRONMENT") == "development"
    )