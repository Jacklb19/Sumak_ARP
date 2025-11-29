from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Crear app
app = FastAPI(
    title="Tech Recruiter Backend - Rol 1",
    description="API Backend para agente de reclutamiento inteligente",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# ============================================================
# IMPORTAR RUTAS
# ============================================================

# Auth routes
from app.api.routes import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Company routes
from app.api.routes import companies
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])

# Job Postings routes
from app.api.routes import jobs
app.include_router(jobs.router, prefix="/api/v1/job-postings", tags=["Job Postings"])

# Applications routes
from app.api.routes import applications
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])

# Scoring routes
from app.api.routes import scoring
app.include_router(scoring.router, prefix="/api/v1/scoring", tags=["Scoring"])

# Webhooks routes
from app.api.routes import webhooks
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

# Chat Agent routes
from app.api.routes import chat
app.include_router(chat.router, prefix="/api/v1/agent", tags=["Agent Chat"])

# Onboarding routes
from app.api.routes import onboarding
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])

# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tech Recruiter Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )