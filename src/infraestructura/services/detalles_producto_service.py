from typing import Optional

from ..models.detalles_producto import detalles_producto
from ..repositories.detalles_producto_repository import (
    actualizarDetalleProducto, obtenerDetalleProducto)


def build_detalles_producto_entity(payload: dict) -> detalles_producto:
    # Asegura que el payload contenga las columnas requeridas por la BD.
    valid_fields = {key: value for key, value in payload.items() if key in detalles_producto.__annotations__}
    return detalles_producto(**valid_fields)


async def obtener_detalles_productos(
    filtros: dict = None, 
    columnas: str = '*', 
    include_producto: bool = False,
    include_precios: bool = False,
    filtros_producto: Optional[dict] = None,
    limite: int = 100,
    offset: int = 0,
):
    return await obtenerDetalleProducto(
        columnas=columnas, 
        filtros=filtros, 
        include_producto=include_producto,
        include_precios=include_precios,
        filtros_producto=filtros_producto,
        limite=limite,
        offset=offset,
    )


async def crear_detalles_producto(payload: dict):
    detalles_producto = build_detalles_producto_entity(payload)

    # Asegurar FK obligatoria.
    # (id_productofk es requerido en el dataclass/request, pero por seguridad validamos)
    if getattr(detalles_producto, 'id_productofk', None) is None:
        raise ValueError('id_productofk es requerido')

    return await actualizarDetalleProducto(detalles_producto)


async def actualizar_detalles_producto(cod_barra: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarDetalleProducto(payload, cod_barra)
