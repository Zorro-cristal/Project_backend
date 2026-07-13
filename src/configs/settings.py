from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Supabase Storage (modelo predicción ventas)
    SUPABASE_STORAGE_BUCKET_VENTAS_MODELS: str = "modelos"
    SUPABASE_STORAGE_OBJECT_VENTAS_MODEL: str = "ventas_prediccion/ventas_model.joblib"

    # Supabase Storage (modelo predicción tiempo ocupación mesas)
    SUPABASE_STORAGE_BUCKET_MESAS_MODELS: str = "modelos"
    SUPABASE_STORAGE_OBJECT_MESAS_MODEL: str = "mesas_prediccion/mesas_model.joblib"

    # App
    APP_NAME: str = "FastAPI Functional"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_super_segura_aqui" # Cambiar por variable de entorno
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # CORS - Lista explícita sin wildcards para permitir credentials
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://projectfrontend-psi.vercel.app,https://project-backend-gamma-seven.vercel.app"
    
# Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Empresa Ubicación (coordenadas para clima)
    EMPRESA_LATITUD: float = -25.2637  # Asunción, Paraguay
    EMPRESA_LONGITUD: float = -57.5759
    
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
