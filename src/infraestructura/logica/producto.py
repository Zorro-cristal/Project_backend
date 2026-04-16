from src.infraestructura.database.producto import (actualizarProducto,
                                                   obtenerProducto)
from src.infraestructura.entidad.producto import Producto


def build_producto_entity(payload: dict) -> Producto:
    valid_fields = {key: value for key, value in payload.items() if key in Producto.__annotations__}
    return Producto(**valid_fields)


async def obtener_productos(columns: str = '*, marcas(marca_id:id, marca_nombre:nombre, marca_estado:estado)'):
    return await obtenerProducto(columnas=columns)


async def crear_producto(payload: dict):
    producto = build_producto_entity(payload)
    return await actualizarProducto(producto)


async def actualizar_producto(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarProducto(payload, id)
