from src.infraestructura.database.detalle_producto import actualizarDetalleProducto, obtenerDetalleProducto
from src.infraestructura.entidad.detalle_producto import Detalle_producto

def build_detalle_producto_entity(payload: dict) -> Detalle_producto:
    valid_fields = {key: value for key, value in payload.items() if key in Detalle_producto.__annotations__}
    return Detalle_producto(**valid_fields)


async def obtener_detalle_productos(filtros: dict= None, columnas: str = '*'):
    return await obtenerDetalleProducto(columnas=columnas, filtros=filtros)


async def crear_detalle_producto(payload: dict):
    detalle_producto = build_detalle_producto_entity(payload)
    return await actualizarDetalleProducto(detalle_producto)


async def actualizar_detalle_producto(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarDetalleProducto(payload, id)
