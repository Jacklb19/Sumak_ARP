
import os
from dotenv import load_dotenv

print("\n" + "="*60)
print("🔍 VALIDADOR DE CREDENCIALES - .env")
print("="*60 + "\n")

# Cargar .env
load_dotenv()

errors = []
warnings = []

# 1. Verificar SUPABASE_URL
supabase_url = os.getenv('SUPABASE_URL', '').strip()
if not supabase_url:
    errors.append("❌ SUPABASE_URL no está definida")
elif not supabase_url.startswith('https://'):
    errors.append("❌ SUPABASE_URL debe empezar con https://")
elif 'supabase.co' not in supabase_url:
    errors.append("❌ SUPABASE_URL debe contener 'supabase.co'")
else:
    print(f"✅ SUPABASE_URL: {supabase_url[:40]}...")

# 2. Verificar SUPABASE_ANON_KEY
anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
if not anon_key:
    errors.append("❌ SUPABASE_ANON_KEY no está definida")
elif not anon_key.startswith('eyJ'):
    errors.append("❌ SUPABASE_ANON_KEY debe empezar con 'eyJ' (JWT)")
elif len(anon_key) < 50:
    errors.append("❌ SUPABASE_ANON_KEY parece muy corta")
else:
    print(f"✅ SUPABASE_ANON_KEY: {anon_key[:40]}...")

# 3. Verificar SUPABASE_SERVICE_ROLE_KEY
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip()
if not service_key:
    errors.append("❌ SUPABASE_SERVICE_ROLE_KEY no está definida")
elif not service_key.startswith('eyJ'):
    errors.append("❌ SUPABASE_SERVICE_ROLE_KEY debe empezar con 'eyJ' (JWT)")
elif len(service_key) < 50:
    errors.append("❌ SUPABASE_SERVICE_ROLE_KEY parece muy corta")
else:
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {service_key[:40]}...")

# 4. Verificar GROQ_API_KEY
groq_key = os.getenv('GROQ_API_KEY', '').strip()
if not groq_key:
    errors.append("❌ GROQ_API_KEY no está definida")
elif not groq_key.startswith('gsk_'):
    errors.append("❌ GROQ_API_KEY debe empezar con 'gsk_'")
elif len(groq_key) < 30:
    errors.append("❌ GROQ_API_KEY parece muy corta")
else:
    print(f"✅ GROQ_API_KEY: {groq_key[:30]}...")

# 5. Verificar SECRET_KEY
secret_key = os.getenv('SECRET_KEY', '').strip()
if not secret_key:
    errors.append("❌ SECRET_KEY no está definida")
elif len(secret_key) < 32:
    errors.append(f"❌ SECRET_KEY debe tener mín 32 caracteres (tiene {len(secret_key)})")
else:
    print(f"✅ SECRET_KEY: {len(secret_key)} caracteres")

# 6. Verificar DEBUG
debug = os.getenv('DEBUG', '').strip()
if debug.lower() in ['true', 'false']:
    print(f"✅ DEBUG: {debug}")
else:
    warnings.append(f"⚠️  DEBUG debe ser 'True' o 'False' (está '{debug}')")

print("\n" + "-"*60)

# Mostrar errores
if errors:
    print("\n❌ ERRORES ENCONTRADOS:\n")
    for error in errors:
        print(f"  {error}")
    print("\n💡 Solución:")
    print("  1. Abre Backend/.env")
    print("  2. Verifica cada credencial en el dashboard de Supabase")
    print("  3. Copia exacto (sin espacios, sin comillas)")
    print("  4. Guarda y reinicia el servidor\n")
else:
    print("\n✅ TODAS LAS VARIABLES ESTÁN BIEN\n")

# Mostrar warnings
if warnings:
    print("⚠️  ADVERTENCIAS:\n")
    for warning in warnings:
        print(f"  {warning}\n")

print("-"*60)

# Intentar conectar a Supabase
if not errors:
    print("\n🔗 INTENTANDO CONEXIÓN A SUPABASE...\n")
    
    try:
        from supabase import create_client
        
        client = create_client(supabase_url, anon_key)
        response = client.table("companies").select("count").execute()
        
        print("✅ CONEXIÓN A SUPABASE EXITOSA")
        print(f"   Total companies: {len(response.data)}")
        print("\n🎉 ¡TODO ESTÁ CONFIGURADO CORRECTAMENTE!")
        print("\n   Próximo paso: python test_backend.py\n")
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ ERROR AL CONECTAR: {e}\n")
        
        if "invalid api key" in error_msg:
            print("💡 Solución:")
            print("  - Verifica SUPABASE_ANON_KEY en dashboard")
            print("  - Copia exacto (sin espacios)")
            print("  - Reinicia servidor\n")
        elif "connection" in error_msg or "network" in error_msg:
            print("💡 Solución:")
            print("  - Verifica conexión a internet")
            print("  - Verifica SUPABASE_URL\n")
        elif "404" in error_msg:
            print("💡 Solución:")
            print("  - Verifica que la tabla 'companies' existe")
            print("  - Ejecuta schema.sql en Supabase SQL Editor\n")

else:
    print("\n⚠️  NO SE PUEDE VALIDAR SUPABASE (hay errores en .env)\n")

print("="*60 + "\n")