from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # App
    APP_NAME: str = "FastAPI Functional"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # CORS - Lista explícita sin wildcards para permitir credentials
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://projectfrontend-psi.vercel.app"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        """Convierte la cadena de orígenes separados por coma en lista"""
        if not self.ALLOWED_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

@lru_cache()
def get_settings() -> Settings:
    return Settings()
