from fastapi import APIRouter

from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica
from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

from . import caja_api as caja
from . import categoria_api as categoria
from . import cliente_api as cliente
from . import compra_api as compra
from . import detalle_compra_api as detalle_compra
from . import detalle_venta_api as detalle_venta
from . import detalles_producto_api as detalles_producto
from . import ingrediente_api as ingrediente
from . import local_api as local
from . import marca_api as marca
from . import mesa_api as mesa
from . import orden_api as orden
from . import permiso_api as permiso
from . import permiso_rol_api as permiso_rol
from . import persona_api as persona
from . import precio_api as precio
from . import producto_api as producto
from . import proveedor_api as proveedor
from . import reserva_api as reserva
from . import rol_api as rol
from . import stock_api as stock
from . import usuario_api as usuario
from . import vendedor_api as vendedor
from . import venta_api as venta

router = APIRouter()


@router.get("/health", summary="Verificar salud del servicio", description="Verifica la conexión a la base de datos y el estado general del servicio.")
async def root():
    result = await conexion_supabase(True)
    return result



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
router.include_router(detalles_producto.router, prefix="/detalles_producto", tags=["Detalle Producto"])
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
router.include_router(orden.router, prefix="/orden", tags=["Orden"])
router.include_router(reserva.router, prefix="/reserva", tags=["Reserva"])


