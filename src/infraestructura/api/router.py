from fastapi import APIRouter

from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica
from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

from . import (caja_api, categoria_api, cliente_api, compra_api,
               cuota_venta_api, cuota_compra_api, detalle_compra_api, detalle_venta_api,
               detalles_producto_api, egreso_api, ingrediente_api, local_api,
               marca_api, mesa_api, orden_api, pago_venta_api, pago_compra_api, permiso_api,
               permiso_rol_api, persona_api, precio_api, producto_api,
               proveedor_api, reserva_api, rol_api, stock_api, usuario_api,
               vendedor_api, venta_api)

router = APIRouter()


@router.get("/health", summary="Verificar salud del servicio", description="Verifica la conexión a la base de datos y el estado general del servicio.")
async def root():
    result = await conexion_supabase(True)
    return result



@router.get("/weather", summary="Obtener información climática", description="Obtiene datos climáticos actuales para una ubicación específica.")
async def pruebaClima():
    result = obtenerInformacionClimatica(-25.801843, -56.437743, ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"])
    return {"message": result} 

router.include_router(usuario_api.router, prefix="/usuario", tags=["Usuario"])
router.include_router(producto_api.router, prefix="/producto", tags=["Producto"])
router.include_router(categoria_api.router, prefix="/categoria", tags=["Categoria"])
router.include_router(marca_api.router, prefix="/marca", tags=["Marca"])
router.include_router(precio_api.router, prefix="/precio", tags=["Precio"])
router.include_router(ingrediente_api.router, prefix="/ingrediente", tags=["Ingrediente"])
router.include_router(rol_api.router, prefix="/rol", tags=["Rol"])
router.include_router(permiso_api.router, prefix="/permiso", tags=["Permiso"])
router.include_router(permiso_rol_api.router, prefix="/permiso_rol", tags=["Permiso Rol"])
router.include_router(detalles_producto_api.router, prefix="/detalles_producto", tags=["Detalle Producto"])
router.include_router(cliente_api.router, prefix="/cliente", tags=["Cliente"])
router.include_router(persona_api.router, prefix="/persona", tags=["Persona"])
router.include_router(vendedor_api.router, prefix="/vendedor", tags=["Vendedor"])
router.include_router(proveedor_api.router, prefix="/proveedor", tags=["Proveedor"])
router.include_router(local_api.router, prefix="/local", tags=["Local"])
router.include_router(mesa_api.router, prefix="/mesa", tags=["Mesa"])
router.include_router(stock_api.router, prefix="/stock", tags=["Stock"])
router.include_router(caja_api.router, prefix="/caja", tags=["Caja"])
router.include_router(venta_api.router, prefix="/venta", tags=["Venta"])
router.include_router(detalle_venta_api.router, prefix="/detalle_venta", tags=["Detalle Venta"])
router.include_router(egreso_api.router, prefix="/egreso", tags=["Egreso"])

router.include_router(compra_api.router, prefix="/compra", tags=["Compra"])
router.include_router(detalle_compra_api.router, prefix="/detalle_compra", tags=["Detalle Compra"])
router.include_router(orden_api.router, prefix="/orden", tags=["Orden"])
router.include_router(reserva_api.router, prefix="/reserva", tags=["Reserva"])

# Nuevos routers para ventas con crédito
router.include_router(cuota_venta_api.router, prefix="/cuota_venta", tags=["Cuota Venta"])
router.include_router(pago_venta_api.router, prefix="/pago_venta", tags=["Pago Venta"])

# Nuevos routers para compras con crédito
router.include_router(cuota_compra_api.router, prefix="/cuota_compra", tags=["Cuota Compra"])
router.include_router(pago_compra_api.router, prefix="/pago_compra", tags=["Pago Compra"])
