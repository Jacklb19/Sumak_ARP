"""Test de configuración."""

import sys
import os

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings

print("=== Testing Configuration ===\n")

print(f"✅ Environment: {settings.environment}")
print(f"✅ API Host: {settings.api_host}:{settings.api_port}")
print(f"✅ Gemini Model: {settings.gemini_model}")
print(f"✅ Temperature: {settings.gemini_temperature}")

# Verificar que las credenciales estén configuradas
try:
    assert settings.google_api_key, "❌ GOOGLE_API_KEY no configurada"
    print(f"✅ Google API Key: {settings.google_api_key[:20]}...")
    
    assert settings.supabase_url, "❌ SUPABASE_URL no configurada"
    print(f"✅ Supabase URL: {settings.supabase_url}")
    
    assert settings.supabase_key, "❌ SUPABASE_KEY no configurada"
    print(f"✅ Supabase Key: {settings.supabase_key[:20]}...")
    
    print("\n🎉 ¡Configuración correcta!")
    
except AssertionError as e:
    print(f"\n❌ {e}")
    exit(1)
