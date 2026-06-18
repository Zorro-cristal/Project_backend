import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware as CORSMiddleware
from fastapi.responses import JSONResponse

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

# Orígenes permitidos - fallback seguro
origins = settings.ALLOWED_ORIGINS_LIST
if not origins or origins == ["*"]:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://projectfrontend-psi.vercel.app",
        "https://project-backend-gamma-seven.vercel.app"
    ]
    logger.warning(f"CORS using FALLBACK origins: {origins}")
else:
    # Asegurar que siempre incluya localhost
    if "http://localhost:5173" not in origins:
        origins.append("http://localhost:5173")
        logger.warning(f"CORS added localhost: {origins}")

logger.info(f"Final CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Se incluyen las rutas
app.include_router(api_router)
