from supabase import create_client, Client
from functools import lru_cache
from src.configs.settings import get_settings

@lru_cache()
def get_supabase_client() -> Client:
    """Retorna cliente de Supabase (singleton)"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)