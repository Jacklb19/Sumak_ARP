"""Test Google Gemini API."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

print(f"✅ API Key: {api_key[:20]}...")
print(f"🤖 Modelo: {model_name}\n")

print("🧪 Test 1: Respuesta Simple\n")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    response = model.generate_content("Di 'Hola' en una palabra")
    print(f"✅ Respuesta: {response.text}\n")
    
    print("🧪 Test 2: Pregunta de Entrevista\n")
    
    prompt = """Eres un entrevistador técnico.
Genera UNA pregunta sobre Python.

Formato:
QUESTION: [pregunta]
"""
    
    response = model.generate_content(prompt)
    print(f"✅ Pregunta generada:\n{response.text}\n")
    
    print("🎉 ¡Google Gemini funciona perfectamente!")
    print("\n📊 Información:")
    print(f"   Modelo: {model_name}")
    print(f"   Gratis: ✅ Sí (15 req/min)")
    print(f"   Costo: $0.00 USD")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
