
from fastapi import FastAPI
from src.infraestructura.routes.demo import router as api_router

app = FastAPI()

# Se incluyen las rutas
app.include_router(api_router)