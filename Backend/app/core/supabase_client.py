from supabase import create_client, Client
from app.core.config import settings
import httpx


class SupabaseClient:
    """Cliente singleton para Supabase con soporte para service role"""
    
    _instance = None
    _client = None  # Cliente normal (anon key)
    _admin_client = None  # Cliente admin (service role key)
    
    @classmethod
    def get_client(cls, use_service_role: bool = False) -> Client:
        """
        Obtener instancia del cliente Supabase
        
        Args:
            use_service_role: Si True, usa service_role_key (bypass RLS)
                            Si False, usa anon_key (con RLS)
        
        Returns:
            Cliente Supabase
        """
        if cls._instance is None:
            cls._instance = cls()
            
            try:
                # Cliente normal con anon key
                cls._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                
                # Cliente admin con service role key (bypass RLS)
                cls._admin_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                
            except TypeError as e:
                if "proxy" in str(e).lower():
                    http_client = httpx.Client()
                    cls._client = create_client(
                        settings.SUPABASE_URL,
                        settings.SUPABASE_ANON_KEY,
                        options={"http_client": http_client}
                    )
                    cls._admin_client = create_client(
                        settings.SUPABASE_URL,
                        settings.SUPABASE_SERVICE_ROLE_KEY,
                        options={"http_client": http_client}
                    )
                else:
                    raise
        
        # Retornar el cliente apropiado
        return cls._admin_client if use_service_role else cls._client
    
    @classmethod
    def close(cls):
        """Cerrar conexiones"""
        cls._instance = None
        cls._client = None
        cls._admin_client = None
