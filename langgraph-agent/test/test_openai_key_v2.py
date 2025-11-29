"""Test de OpenAI API Key - Auto-detecta modelo disponible."""

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

# Lista de modelos a probar (en orden de preferencia)
models_to_try = [
    "gpt-4-turbo",      # Mejor pero requiere acceso
    "gpt-4o-mini",      # GPT-4 mini (más barato)
    "gpt-3.5-turbo",    # Más barato y disponible para todos
]

print("\n🧪 Testing modelos disponibles...\n")

for model in models_to_try:
    try:
        print(f"Probando {model}...", end=" ")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Responde solo: OK"}
            ],
            max_tokens=10
        )
        
        message = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        # Calcular costo aproximado
        if "gpt-4" in model:
            cost = tokens * 0.00003  # GPT-4 aprox
        else:
            cost = tokens * 0.000002  # GPT-3.5 aprox
        
        print(f"✅ FUNCIONA")
        print(f"   Respuesta: {message}")
        print(f"   Tokens: {tokens}")
        print(f"   Costo: ${cost:.6f} USD")
        print(f"\n🎉 ¡Modelo recomendado: {model}!")
        print(f"\n📝 Actualiza tu .env con:")
        print(f"   OPENAI_MODEL={model}")
        break
        
    except Exception as e:
        if "model_not_found" in str(e) or "does not exist" in str(e):
            print("❌ No disponible")
        else:
            print(f"❌ Error: {e}")
            break
else:
    print("\n❌ Ningún modelo disponible. Verifica tu API key.")
