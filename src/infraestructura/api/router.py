from fastapi import APIRouter

from src.infraestructura.api import caja_api as caja
from src.infraestructura.api import categoria_api as categoria
from src.infraestructura.api import cliente_api as cliente
from src.infraestructura.api import compra_api as compra
from src.infraestructura.api import detalle_compra_api as detalle_compra
from src.infraestructura.api import detalle_producto_api as detalle_producto
from src.infraestructura.api import detalle_venta_api as detalle_venta
from src.infraestructura.api import ingrediente_api as ingrediente
from src.infraestructura.api import local_api as local
from src.infraestructura.api import marca_api as marca
from src.infraestructura.api import mesa_api as mesa
from src.infraestructura.api import permiso_api as permiso
from src.infraestructura.api import permiso_rol_api as permiso_rol
from src.infraestructura.api import persona_api as persona
from src.infraestructura.api import precio_api as precio
from src.infraestructura.api import producto_api as producto
from src.infraestructura.api import proveedor_api as proveedor
from src.infraestructura.api import rol_api as rol
from src.infraestructura.api import stock_api as stock
from src.infraestructura.api import usuario_api as usuario
from src.infraestructura.api import vendedor_api as vendedor
from src.infraestructura.api import venta_api as venta
from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica
from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

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
