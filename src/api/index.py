import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORSMiddleware

from src.configs.settings import get_settings
from src.infraestructura.api.router import router as api_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI()

# Orígenes permitidos desde configuración - permite credentials=True
# IMPORTANTE: No usar "*" cuando allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se incluyen las rutas
app.include_router(api_router)
