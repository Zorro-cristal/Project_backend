from fastapi import APIRouter

from src.infraestructura.routes import (categoria, marca, precio, producto,
                                        usuario, ingrediente, rol)
from src.shell.adaptadores.externals.openmeteo import \
    obtenerInformacionClimatica
from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

router = APIRouter()

@router.get("/health", summary="Verificar salud del servicio", description="Verifica la conexión a la base de datos y el estado general del servicio.")
async def root():
    result = await conexion_supabase(True)
    return {"message": result} 

@router.get("/weather", summary="Obtener información climática", description="Obtiene datos climáticos actuales para una ubicación específica.")
async def pruebaClima():
    result = obtenerInformacionClimatica(-25.801843, -56.437743, ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"])
    return {"message": result} 

router.include_router(usuario.router, prefix="/usuario", tags=["Usuario"])
router.include_router(producto.router, prefix="/producto", tags=["Producto"])
router.include_router(categoria.router, prefix="/categoria", tags=["Categoria"])
router.include_router(marca.router, prefix="/marca", tags=["Marca"])
router.include_router(precio.router, prefix="/precio", tags=["Precio"])
router.include_router(ingrediente.router, prefix="/ingrediente", tags=["Ingrediente"])
router.include_router(rol.router, prefix="/rol", tags=["Rol"])