from fastapi import APIRouter

from src.infraestructura.api import (categoria_api as categoria, marca_api as marca, precio_api as precio, producto_api as producto,
                                        usuario_api as usuario, ingrediente_api as ingrediente, rol_api as rol, detalle_producto_api as detalle_producto, cliente_api as cliente, persona_api as persona, permiso_api as permiso, permiso_rol_api as permiso_rol, vendedor_api as vendedor, proveedor_api as proveedor, local_api as local, mesa_api as mesa, stock_api as stock, caja_api as caja, venta_api as venta, detalle_venta_api as detalle_venta, compra_api as compra, detalle_compra_api as detalle_compra)
from src.shell.adapters.externals.openmeteo import \
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
router.include_router(permiso.router, prefix="/permiso", tags=["Permiso"])
router.include_router(permiso_rol.router, prefix="/permiso_rol", tags=["Permiso Rol"])
router.include_router(detalle_producto.router, prefix="/detalle_producto", tags=["Detalle Producto"])
router.include_router(cliente.router, prefix="/cliente", tags=["Cliente"])
router.include_router(persona.router, prefix="/persona", tags=["Persona"])
router.include_router(vendedor.router, prefix="/vendedor", tags=["Vendedor"])
router.include_router(proveedor.router, prefix="/proveedor", tags=["Proveedor"])
router.include_router(local.router, prefix="/local", tags=["Local"])
router.include_router(mesa.router, prefix="/mesa", tags=["Mesa"])
router.include_router(stock.router, prefix="/stock", tags=["Stock"])
router.include_router(caja.router, prefix="/caja", tags=["Caja"])
router.include_router(venta.router, prefix="/venta", tags=["Venta"])
router.include_router(detalle_venta.router, prefix="/detalle_venta", tags=["Detalle Venta"])
router.include_router(compra.router, prefix="/compra", tags=["Compra"])
router.include_router(detalle_compra.router, prefix="/detalle_compra", tags=["Detalle Compra"])
