from src.infraestructura.services.venta_service import \
    obtener_detalle_venta_por_venta_id as \
    obtener_detalle_venta_por_venta_id_service
from src.infraestructura.services.venta_service import \
    obtener_venta_por_id_con_detalles as \
    obtener_venta_por_id_con_detalles_service
from src.infraestructura.services.venta_service import \
    obtener_venta_por_id_sin_detalles as \
    obtener_venta_por_id_sin_detalles_service
from src.infraestructura.services.venta_service import \
    obtener_ventas as obtener_ventas_service


async def obtener_ventas(filtros: dict = None):
    return await obtener_ventas_service(filtros)


async def obtener_venta_por_id_sin_detalles(filtros: dict = None):
    return await obtener_venta_por_id_sin_detalles_service(filtros)


async def obtener_venta_por_id_con_detalles(filtros: dict = None):
    return await obtener_venta_por_id_con_detalles_service(filtros)


async def obtener_detalle_venta_por_venta_id(filtros: dict = None):
    return await obtener_detalle_venta_por_venta_id_service(filtros)
