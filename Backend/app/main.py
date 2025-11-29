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
# IMPORTAR RUTAS (forma explícita)
# ============================================================

from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as companies_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.applications import router as applications_router
from app.api.routes.scoring import router as scoring_router
from app.api.routes.webhooks import router as webhooks_router
from app.api.routes.chat import router as chat_router
from app.api.routes.onboarding import router as onboarding_router

# Registrar routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(companies_router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(jobs_router, prefix="/api/v1/job-postings", tags=["Job Postings"])
app.include_router(applications_router, prefix="/api/v1/applications", tags=["Applications"])
app.include_router(scoring_router, prefix="/api/v1/scoring", tags=["Scoring"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(chat_router, prefix="/api/v1/agent", tags=["Agent Chat"])
app.include_router(onboarding_router, prefix="/api/v1/onboarding", tags=["Onboarding"])


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
