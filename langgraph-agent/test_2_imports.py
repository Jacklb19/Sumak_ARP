"""Test básico de imports."""

print("🧪 Testing imports...\n")

try:
    # Config
    from config import settings
    print("✅ config.settings")
    
    # Models
    from models import InterviewState, InterviewStepRequest
    print("✅ models")
    
    # Services
    from services.llm_service import generate_question
    print("✅ services.llm_service")
    
    from services.supabase_client import get_job_posting
    print("✅ services.supabase_client")
    
    # Nodes
    from nodes import initialize_interview, knockout_phase
    print("✅ nodes")
    
    # Graph
    from graph import interview_graph
    print("✅ graph")
    
    # External libs
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ langchain_google_genai")
    
    import google.generativeai as genai
    print("✅ google.generativeai")
    
    from langgraph.graph import StateGraph
    print("✅ langgraph")
    
    print("\n🎉 ¡Todos los imports funcionan!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
