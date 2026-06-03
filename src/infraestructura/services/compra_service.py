from typing import Optional

from ..models.compra import Compra
from ..repositories.compra_repository import actualizarCompra, obtenerCompra
from ..repositories.detalle_compra_repository import obtenerDetalleCompra


def build_compra_entity(payload: dict) -> Compra:
    valid_fields = {key: value for key, value in payload.items() if key in Compra.__annotations__}
    return Compra(**valid_fields)


async def obtener_compras(filtros: dict = None, columnas: str = '*'):
    return await obtenerCompra(filtros=filtros, columnas=columnas)


async def obtener_compra_solo(id: int, columnas: str = '*'):
    compras = await obtenerCompra(filtros={"id": id}, columnas=columnas)
    if not compras:
        return None
    if isinstance(compras, list):
        return compras[0] if compras else None
    return compras


async def obtener_compra_detalles(id: int):
    return await obtenerDetalleCompra(filtros={"id_comprafk": id})


async def crear_compra(payload: dict):
    compra = build_compra_entity(payload)
    return await actualizarCompra(compra)


async def actualizar_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarCompra(payload, id)
