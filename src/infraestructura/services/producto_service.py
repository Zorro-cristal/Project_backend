from src.infraestructura.models.producto import Producto
from src.infraestructura.repositories.producto_repository import (
    actualizarProducto, obtenerDetallesProducto, obtenerProducto,
    obtenerProductoConDetallesProducto)


def build_producto_entity(payload: dict) -> Producto:
    valid_fields = {key: value for key, value in payload.items() if key in Producto.__annotations__}
    return Producto(**valid_fields)


async def obtener_productos(filtros=None, columnas: str = '*'):
    return await obtenerProducto(filtros=filtros, columnas=columnas)


async def obtener_producto(id: int, include_detallesProducto: bool = False):
    if include_detallesProducto:
        return await obtenerProductoConDetallesProducto(id)
    return await obtenerProducto(filtros={"id": id}, columnas='*, marcas(id_marcafk:id, marca_nombre:nombre, marca_estado:estado)')


async def obtener_detallesProducto(id: int):
    return await obtenerDetallesProducto(id)



async def crear_producto(payload: dict):
    producto = build_producto_entity(payload)
    return await actualizarProducto(producto)


async def actualizar_producto(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarProducto(payload, id)

