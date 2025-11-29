from supabase import create_client, Client
from app.core.config import settings
from typing import Optional


class SupabaseClient:
    """
    Cliente Supabase singleton
    """
    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Retorna instancia singleton de Supabase
        """
        if cls._instance is None:
            cls._instance = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
            )
        return cls._instance

    @classmethod
    def get_anon_client(cls) -> Client:
        """
        Cliente anónimo para operaciones públicas
        """
        return create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY
        )


# Usar: from app.core.supabase_client import SupabaseClient
# client = SupabaseClient.get_client()