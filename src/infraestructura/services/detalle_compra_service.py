from src.shell.utils import attach_related

from ..models.detalle_compra import Detalle_compra
from ..repositories.detalle_compra_repository import (actualizarDetalleCompra,
                                                      obtenerDetalleCompra)
from .producto_service import obtener_productos


def build_detalle_compra_entity(payload: dict) -> Detalle_compra:
    valid_fields = {key: value for key, value in payload.items() if key in Detalle_compra.__annotations__}
    return Detalle_compra(**valid_fields)


async def attach_related_data(detalles: list[dict]) -> list[dict]:
    return await attach_related(detalles, 'id_productofk', obtener_productos, 'id', 'id', 'producto')


async def obtener_detalle_compras(filtros: dict = None, columnas: str = '*'):
    detalles = await obtenerDetalleCompra(filtros=filtros, columnas=columnas)
    if not detalles:
        return detalles
    return await attach_related_data(detalles)


async def crear_detalle_compra(payload: dict):
    detalle = build_detalle_compra_entity(payload)
    return await actualizarDetalleCompra(detalle)


async def actualizar_detalle_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarDetalleCompra(payload, id)
