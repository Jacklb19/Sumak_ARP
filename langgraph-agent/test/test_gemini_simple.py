"""Test Google Gemini con modelo correcto."""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY no encontrada en .env")
    exit(1)

print(f"✅ API Key: {api_key[:20]}...")

# Lista de modelos a probar
models_to_try = [
    "gemini-pro",           # Modelo estable
    "gemini-1.5-pro",       # Más reciente
    "gemini-1.0-pro",       # Alternativa
]

print("\n🧪 Probando modelos disponibles...\n")

import google.generativeai as genai
genai.configure(api_key=api_key)

for model_name in models_to_try:
    try:
        print(f"Probando {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Di 'OK' en una palabra")
        
        print(f"✅ FUNCIONA")
        print(f"   Respuesta: {response.text}")
        print(f"\n🎉 ¡Modelo recomendado: {model_name}!")
        print(f"\n📝 Actualiza tu .env con:")
        print(f"   GEMINI_MODEL={model_name}")
        break
        
    except Exception as e:
        if "not found" in str(e) or "not supported" in str(e):
            print("❌ No disponible")
        else:
            print(f"❌ Error: {e}")
            break
else:
    print("\n⚠️ Probando con lista de modelos...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Disponible: {m.name}")
    except Exception as e:
        print(f"Error listando modelos: {e}")
