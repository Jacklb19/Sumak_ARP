# Backend - Rol 1 (Tech Recruiter)

## Descripción

Este es el **Backend API** (Rol 1) del sistema de reclutamiento inteligente. Implementa:

- ✅ Autenticación y gestión de empresas
- ✅ CRUD de vacantes y candidatos
- ✅ Parseo de CV + generación de embeddings
- ✅ Cálculo de scores (CV, técnico, soft skills)
- ✅ Webhooks para integración con n8n
- ✅ Chat con agente analista
- ✅ Generación de emails de onboarding

Stack: **FastAPI** + **Supabase** + **OpenAI** + **Python**

---

## Setup Local

### 1. Requisitos previos

- Python 3.11+
- pip o poetry
- Supabase account (supabase.co)
- OpenAI API key

### 2. Clonar y preparar

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Variables de entorno

Copiar `.env.example` a `.env` y rellenar:

```bash
cp .env.example .env
```

```env
# SUPABASE
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# OPENAI
OPENAI_API_KEY=sk-...

# JWT
SECRET_KEY=tu-super-secret-key-minimo-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Backend
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

### 4. Base de datos (Supabase)

1. Crear proyecto en Supabase
2. Ejecutar SQL en el SQL Editor:

```bash
# Copiar contenido de database/schema.sql
# Pegar en Supabase SQL Editor
# Ejecutar
```

Esto crea:
- Tablas: companies, job_postings, candidates, applications, etc.
- Índices para performance
- RLS (Row Level Security) para privacidad

### 5. Ejecutar servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Servidor activo en: **http://localhost:8000**

📚 Documentación Swagger: **http://localhost:8000/docs**

---

## Estructura de carpetas

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── auth.py              # Autenticación
│   │   ├── companies.py         # Empresas
│   │   ├── jobs.py              # Vacantes
│   │   ├── applications.py      # Postulaciones
│   │   ├── scoring.py           # Scores
│   │   ├── webhooks.py          # Webhooks n8n
│   │   ├── chat.py              # Chat agente
│   │   └── onboarding.py        # Onboarding
│   ├── core/
│   │   ├── config.py            # Configuración
│   │   ├── security.py          # JWT + Auth
│   │   └── supabase_client.py   # Cliente DB
│   ├── models/
│   │   ├── schemas.py           # Pydantic models
│   │   └── enums.py             # Enumeraciones
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── cv_parser.py
│   │   ├── scoring_service.py
│   │   └── llm_service.py
│   ├── utils/
│   │   └── helpers.py
│   └── main.py                  # FastAPI app
├── database/
│   └── schema.sql               # DDL Supabase
├── requirements.txt
├── .env.example
└── README_backend.md
```

---

## API Endpoints

### Auth

```bash
# Registrar empresa
curl -X POST http://localhost:8000/api/v1/auth/register-company \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "email": "hr@techcorp.com",
    "password": "secure123",
    "sector": "Technology",
    "size": "pyme",
    "country": "Colombia"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr@techcorp.com",
    "password": "secure123"
  }'
```

Respuesta:
```json
{
  "success": true,
  "token": "eyJhbGc...",
  "company_id": "uuid-123",
  "user_role": "admin"
}
```

### Empresas

```bash
# Obtener perfil
curl -X GET http://localhost:8000/api/v1/companies/uuid-123 \
  -H "Authorization: Bearer eyJhbGc..."

# Actualizar perfil
curl -X PUT http://localhost:8000/api/v1/companies/uuid-123 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Somos una startup de tech",
    "whatsapp_number": "+573001234567"
  }'
```

### Vacantes

```bash
# Crear vacante
curl -X POST http://localhost:8000/api/v1/job-postings \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "uuid-123",
    "title": "Senior Python Developer",
    "description": "Buscamos un dev senior...",
    "required_skills": {"languages": ["Python", "FastAPI"]},
    "modality": "remote"
  }'

# Listar vacantes publicadas
curl -X GET "http://localhost:8000/api/v1/job-postings?status=published"

# Publicar vacante
curl -X PUT http://localhost:8000/api/v1/job-postings/uuid-456/publish \
  -H "Authorization: Bearer eyJhbGc..."
```

### Postulaciones

```bash
# Crear postulación (con archivo CV)
curl -X POST http://localhost:8000/api/v1/applications \
  -F "full_name=Juan García" \
  -F "email=juan@example.com" \
  -F "phone_number=+573001234567" \
  -F "job_posting_id=uuid-456" \
  -F "cv_file=@/path/to/cv.pdf" \
  -F "consent_ai=true"

# Obtener detalle postulación
curl -X GET http://localhost:8000/api/v1/applications/uuid-789 \
  -H "Authorization: Bearer eyJhbGc..."

# Ver transcripción de chat
curl -X GET http://localhost:8000/api/v1/applications/uuid-789/transcript \
  -H "Authorization: Bearer eyJhbGc..."

# Listar candidatos de una vacante
curl -X GET "http://localhost:8000/api/v1/job-postings/uuid-456/applications?status=evaluation_completed&sort_by=global_score" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Scoring

```bash
# Calcular score de CV
curl -X POST http://localhost:8000/api/v1/scoring/calculate-cv-score \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "uuid-111",
    "job_posting_id": "uuid-456"
  }'

# Calcular score global
curl -X POST http://localhost:8000/api/v1/scoring/calculate-global-score \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "uuid-789",
    "job_posting_id": "uuid-456",
    "cv_score": 82,
    "technical_score": 78,
    "soft_skills_score": 85
  }'
```

### Webhooks (desde n8n)

```bash
# Recibir respuesta de candidato (llamado por n8n)
curl -X POST http://localhost:8000/api/v1/webhooks/interview-step \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "uuid-789",
    "candidate_message": "Tengo 4 años con FastAPI",
    "interview_state": {
      "current_phase": "technical",
      "completed_phases": ["knockout"],
      "conversation_history": [...]
    }
  }'
```

### Chat Agent

```bash
# Chat reclutador con agente
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "job_posting_id": "uuid-456",
    "question": "¿Quiénes son los 3 mejores candidatos?"
  }'
```

### Onboarding

```bash
# Generar email de onboarding
curl -X POST http://localhost:8000/api/v1/onboarding/generate \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "uuid-789",
    "company_info": {"name": "TechCorp"},
    "job_info": {"title": "Senior Developer"}
  }'

# Enviar email
curl -X POST http://localhost:8000/api/v1/onboarding/send \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "onboarding_template_id": "uuid-onb-123"
  }'
```

---

## Testing

Usar **Swagger UI** para probar:
- Abrir http://localhost:8000/docs
- Click en "Try it out" en cada endpoint
- Llenar parámetros
- Ejecutar

---

## Deployment

### Producción

```bash
# Usando Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# O en Railway/Vercel:
# Crear archivo Procfile:
# web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Variables de entorno en producción

Cambiar en `.env`:
```env
DEBUG=False
CORS_ORIGINS=["https://tu-frontend.com"]
OPENAI_MODEL=gpt-4  # o tu modelo preferido
```

---

## Troubleshooting

### Error: "No module named 'app'"

```bash
# Asegúrate de estar en la carpeta backend/
cd backend
# Y que venv esté activado
source venv/bin/activate
```

### Error: "Supabase connection failed"

1. Verifica que SUPABASE_URL y keys sean correctas
2. Revisa que el proyecto exista en supabase.co
3. Que el schema.sql esté ejecutado

### Error: "OpenAI API error"

1. Verifica OPENAI_API_KEY sea válido
2. Que tengas créditos en OpenAI
3. Que el modelo (gpt-4 o gpt-3.5-turbo) esté disponible

---

## Documentación adicional

- [FastAPI docs](https://fastapi.tiangolo.com)
- [Supabase docs](https://supabase.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Documento arquitectura](../../ARQUITECTURA.md)