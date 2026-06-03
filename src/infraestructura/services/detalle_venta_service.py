from src.shell.utils import attach_related

from ..models.detalle_venta import Detalle_venta
from ..repositories.detalle_venta_repository import (actualizarDetalleVenta,
                                                     obtenerDetalleVenta)
from .producto_service import obtener_productos


def build_detalle_venta_entity(payload: dict) -> Detalle_venta:
    valid_fields = {key: value for key, value in payload.items() if key in Detalle_venta.__annotations__}
    return Detalle_venta(**valid_fields)


async def attach_related_data(detalles: list[dict]) -> list[dict]:
    return await attach_related(detalles, 'id_productofk', obtener_productos, 'id', 'id', 'producto')


async def obtener_detalle_ventas(filtros: dict = None, columnas: str = '*'):
    detalles = await obtenerDetalleVenta(filtros=filtros, columnas=columnas)
    if not detalles:
        return detalles
    return await attach_related_data(detalles)


async def crear_detalle_venta(payload: dict):
    detalle = build_detalle_venta_entity(payload)
    return await actualizarDetalleVenta(detalle)


async def actualizar_detalle_venta(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarDetalleVenta(payload, id)
