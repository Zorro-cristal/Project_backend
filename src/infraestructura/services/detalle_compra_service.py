from src.shell.utils import attach_related

from ..models.detalle_compra import Detalle_compra
from ..repositories.detalle_compra_repository import (actualizarDetalleCompra,
                                                      obtenerDetalleCompra)
from .stock_service import obtener_stocks


def build_detalle_compra_entity(payload: dict) -> Detalle_compra:
    valid_fields = {key: value for key, value in payload.items() if key in Detalle_compra.__annotations__}
    return Detalle_compra(**valid_fields)


async def attach_related_data(detalles: list[dict]) -> list[dict]:
    return await attach_related(detalles, 'id_stockfk', obtener_stocks, 'id', 'id', 'stock')


async def obtener_detalle_compras(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    detalles = await obtenerDetalleCompra(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
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
