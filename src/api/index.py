import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from src.configs.settings import get_settings
from src.infraestructura.api.router import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

logger.info(f"CORS Settings - ALLOWED_ORIGINS: '{settings.ALLOWED_ORIGINS}'")
logger.info(f"CORS Settings - ALLOWED_ORIGINS_LIST: {settings.ALLOWED_ORIGINS_LIST}")

fastapi_app = FastAPI()

origins = settings.ALLOWED_ORIGINS_LIST
if not origins or origins == ["*"]:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://projectfrontend-psi.vercel.app",
        "https://project-backend-gamma-seven.vercel.app",
    ]
    logger.warning(f"CORS using FALLBACK origins: {origins}")
elif "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")
    logger.warning(f"CORS added localhost: {origins}")

logger.info(f"Final CORS origins: {origins}")


@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error for {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Error de validación en los datos enviados",
        },
    )


@fastapi_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code} error for {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@fastapi_app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "message": "Ocurrió un error inesperado. Por favor, intente nuevamente.",
        },
    )


@fastapi_app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


fastapi_app.include_router(api_router)

# Wrap the complete ASGI app so CORS headers are also present on unhandled 500s.
app = CORSMiddleware(
    app=fastapi_app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,
)
