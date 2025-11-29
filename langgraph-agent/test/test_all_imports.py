"""Test de imports."""

print("🧪 Testing imports...\n")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ langchain_google_genai")
    
    import google.generativeai as genai
    print("✅ google.generativeai")
    
    from langgraph.graph import StateGraph
    print("✅ langgraph")
    
    from fastapi import FastAPI
    print("✅ fastapi")
    
    print("\n🎉 ¡Todos los imports críticos funcionan!")
    
except Exception as e:
    print(f"❌ Error: {e}")
