from fastapi import APIRouter
from src.shell.adaptadores.externals.openmeteo import obtenerInformacionClimatica
from src.infraestructura.routes import ( marca, precio, usuario, producto, categoria )
from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

router = APIRouter()

@router.get("/health")
async def root():
    result = await conexion_supabase(True)
    return {"message": result} 

@router.get("/weather")
async def pruebaClima():
    result = obtenerInformacionClimatica(-25.801843, -56.437743, ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"])
    return {"message": result} 

router.include_router(usuario.router, prefix="/usuario", tags=["Usuario"])
router.include_router(producto.router, prefix="/producto", tags=["Producto"])
router.include_router(categoria.router, prefix="/categoria", tags=["Categoria"])
router.include_router(marca.router, prefix="/marca", tags=["Marca"])
router.include_router(precio.router, prefix="/precio", tags=["Precio"])