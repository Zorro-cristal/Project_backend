import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORSMiddleware

from src.configs.settings import get_settings
from src.infraestructura.api.router import router as api_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Logging para debuggear CORS
logger.info(f"CORS Settings - ALLOWED_ORIGINS: '{settings.ALLOWED_ORIGINS}'")
logger.info(f"CORS Settings - ALLOWED_ORIGINS_LIST: {settings.ALLOWED_ORIGINS_LIST}")

app = FastAPI()

# Orígenes permitidos desde configuración - permite credentials=True
# IMPORTANTE: No usar "*" cuando allow_credentials=True
# Fallback a localhost si no hay configuración
origins = settings.ALLOWED_ORIGINS_LIST
if not origins or origins == ["*"]:
    # Fallback si la config está vacía
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://projectfrontend-psi.vercel.app",
        "https://project-backend-gamma-seven.vercel.app"
    ]
    logger.warning(f"CORS using FALLBACK origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se incluyen las rutas
app.include_router(api_router)
