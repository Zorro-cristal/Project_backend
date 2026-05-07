
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.configs.settings import get_settings
from src.infraestructura.routes.api import router as api_router

settings = get_settings()
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se incluyen las rutas
app.include_router(api_router)