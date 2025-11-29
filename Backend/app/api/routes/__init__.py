# Puedes dejarlo vacío o importar todos los routers aquí
from . import auth
from . import companies
from . import jobs
from . import applications
from . import scoring
from . import webhooks
from . import chat
from . import onboarding

__all__ = [
    "auth",
    "companies", 
    "jobs",
    "applications",
    "scoring",
    "webhooks",
    "chat",
    "onboarding"
]
