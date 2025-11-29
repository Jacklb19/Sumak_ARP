"""Test de OpenAI API Key."""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar .env
load_dotenv()

# Obtener key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY no encontrada en .env")
    exit(1)

print(f"✅ API Key encontrada: {api_key[:20]}...")

# Crear cliente
client = OpenAI(api_key=api_key)

# Test simple
print("\n🧪 Testing API...")

try:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": "Di 'Hola mundo' en una palabra"}
        ],
        max_tokens=10
    )
    
    message = response.choices[0].message.content
    print(f"✅ Respuesta de OpenAI: {message}")
    print(f"✅ Tokens usados: {response.usage.total_tokens}")
    print(f"✅ Costo aproximado: ${response.usage.total_tokens * 0.00001:.6f} USD")
    print("\n🎉 ¡API Key funciona correctamente!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if "invalid_api_key" in str(e):
        print("\n⚠️ API Key inválida. Verifica que:")
        print("   1. Copiaste la key completa")
        print("   2. No tiene espacios extra")
        print("   3. Está en el archivo .env correcto")
