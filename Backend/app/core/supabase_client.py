from supabase import create_client
from app.core.config import settings
import httpx

class SupabaseClient:
    """Cliente singleton para Supabase - Sin proxy issues"""
    
    _instance = None
    _client = None
    
    @classmethod
    def get_client(cls):
        """Obtener instancia singleton del cliente"""
        if cls._instance is None:
            cls._instance = cls()
            
            try:
                # Intenta crear con configuración normal
                cls._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
            except TypeError as e:
                # Si falla por proxy, crear cliente customizado
                if "proxy" in str(e).lower():
                    # Crear cliente HTTP sin proxy
                    http_client = httpx.Client()
                    cls._client = create_client(
                        settings.SUPABASE_URL,
                        settings.SUPABASE_ANON_KEY,
                        options={"http_client": http_client}
                    )
                else:
                    raise
        
        return cls._client
    
    @classmethod
    def close(cls):
        """Cerrar conexión"""
        cls._instance = None
        cls._client = None