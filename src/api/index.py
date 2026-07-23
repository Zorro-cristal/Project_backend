import logging

from fastapi import FastAPI, Request, Response

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

# NOTA: NO usamos el CORSMiddleware de FastAPI porque en Vercel (serverless)
# serializa incorrectamente la lista de orígenes como string JSON en vez de
# devolver el origen específico de la solicitud. Usamos nuestro propio
# middleware HTTP que maneja correctamente los preflight OPTIONS y asegura
# que TODAS las respuestas tengan las cabeceras CORS correctas.

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# =============================================================================
# MIDDLEWARE ESPECIALIZADO PARA MANEJAR CORS EN VERCEL (SERVERLESS)
# =============================================================================
# En Vercel, el middleware CORS estándar de FastAPI a veces no maneja
# correctamente las solicitudes OPTIONS (preflight). Este middleware:
# 1. Captura solicitudes OPTIONS y responde inmediatamente con cabeceras CORS
# 2. Asegura que TODAS las respuestas incluyan las cabeceras CORS necesarias
# =============================================================================

# Diccionario de orígenes permitidos formateados como cadena separada por comas
ORIGINS_SET = set(origins)
ALLOWED_ORIGINS_STR = ", ".join(origins)


@app.middleware("http")
async def cors_preflight_middleware(request: Request, call_next):
    """Middleware que maneja solicitudes OPTIONS (preflight) y asegura cabeceras CORS en todas las respuestas."""
    
    # Obtener el origen de la solicitud
    request_origin = request.headers.get("origin", "")
    
    # Determinar si el origen está permitido
    if request_origin in ORIGINS_SET or "*" in ORIGINS_SET:
        allow_origin = request_origin
    else:
        allow_origin = origins[0] if origins else "*"
    
    # ==========================================
    # Manejo de solicitudes OPTIONS (preflight)
    # ==========================================
    # En Vercel serverless, las OPTIONS a veces no pasan por el middleware CORS
    # de FastAPI, por lo que interceptamos aquí y respondemos directamente.
    if request.method == "OPTIONS":
        logger.info(f"CORS Preflight: OPTIONS {request.url.path} from origin: {request_origin}")
        return Response(
            status_code=200,
            content="",
            media_type="text/plain",
            headers={
                "Access-Control-Allow-Origin": allow_origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",  # 24 horas en caché
            },
        )
    
    # ==========================================
    # Procesar la solicitud normalmente
    # ==========================================
    response = await call_next(request)
    
    # ==========================================
    # Asegurar cabeceras CORS en la respuesta
    # ==========================================
    # Esto es crítico porque las respuestas de error (401, 403, 404, 500)
    # pueden no tener las cabeceras CORS si son generadas por FastAPI
    # antes de que el middleware CORS estándar las procese.
    # Sin esto, el navegador bloqueará la respuesta aunque el backend
    # haya procesado la solicitud correctamente.
    response.headers["Access-Control-Allow-Origin"] = allow_origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    
    return response


# Se incluyen las rutas
app.include_router(api_router)
