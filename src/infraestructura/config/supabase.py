from functools import lru_cache

from supabase import Client, create_client

from src.configs.settings import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Retorna el cliente opcional de Supabase Storage (singleton)."""
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "Supabase Storage sigue habilitado para modelos; configura SUPABASE_URL "
            "y SUPABASE_KEY o migra los artefactos a otro almacenamiento."
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)