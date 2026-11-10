from src.shell.flujo.producto.crearActualizarProducto import (
    actualizar_producto_por_id, crear_o_actualizar_producto)

from ..models.producto import Producto
from ..repositories.categoria_repository import obtenerCategoria
from ..repositories.marca_repository import obtenerMarca
from ..repositories.producto_repository import (
    obtenerDetallesProducto, obtenerProducto,
    obtenerProductoConDetallesProducto)


class ProductoReferenciaInvalida(ValueError):
    pass


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
    categorias = await obtenerCategoria(
        filtros={"id": producto.id_categoriafk},
        limite=1,
        offset=0,
    )
    if not categorias:
        raise ProductoReferenciaInvalida(
            f"No existe la categoría con id {producto.id_categoriafk}."
        )

    marcas = await obtenerMarca(
        filtros={"id": producto.id_marcafk},
        limite=1,
        offset=0,
    )
    if not marcas:
        raise ProductoReferenciaInvalida(
            f"No existe la marca con id {producto.id_marcafk}."
        )

    return await crear_o_actualizar_producto(producto)


async def actualizar_producto(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizar_producto_por_id(id, payload)
