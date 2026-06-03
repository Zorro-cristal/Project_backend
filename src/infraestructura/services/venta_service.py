from typing import Optional

from ..models.venta import Venta
from ..repositories.detalle_venta_repository import \
    obtenerDetalleVenta
from ..repositories.venta_repository import (actualizarVenta,
                                                               obtenerVenta)
from .cliente_service import obtener_clientes
from .local_service import obtener_locales
from .usuario_service import obtener_usuarios
from src.shell.utils import attach_related, attach_grouped


def build_venta_entity(payload: dict) -> Venta:
    valid_fields = {key: value for key, value in payload.items() if key in Venta.__annotations__}
    return Venta(**valid_fields)


async def attach_related_data(ventas: list[dict]) -> list[dict]:
    # One-to-one
    ventas = await attach_related(ventas, 'id_usuariofk', obtener_usuarios, 'id', 'id', 'usuario')
    ventas = await attach_related(ventas, 'id_clientefk', obtener_clientes, 'id', 'id', 'cliente')
    ventas = await attach_related(ventas, 'id_localfk', obtener_locales, 'id', 'id', 'local')
    # One-to-many detalles
    ventas = await attach_grouped(ventas, 'id', obtenerDetalleVenta, 'id_ventafk', 'id_ventafk', 'detalles')
    return ventas


async def obtener_ventas(filtros: dict = None, columnas: str = '*'):
    """Retorna ventas con relaciones adjuntas (usuario/cliente/local/detalles)."""
    ventas = await obtenerVenta(filtros=filtros, columnas=columnas)
    if not ventas:
        return ventas
    return await attach_related_data(ventas)


async def obtener_venta_por_id_sin_detalles(filtros: dict = None, columnas: str = '*'):
    """Retorna la venta por id sin adjuntar detalle_venta."""
    venta = await obtenerVenta(filtros=filtros, columnas=columnas)
    if not venta:
        return None
    # repository suele retornar lista
    if isinstance(venta, list):
        return venta[0] if venta else None
    return venta


async def obtener_venta_por_id_con_detalles(filtros: dict = None, columnas: str = '*'):
    """Retorna la venta por id con relaciones adjuntas, incluyendo detalles."""
    venta_con_detalles = await obtener_ventas(filtros=filtros, columnas=columnas)
    if not venta_con_detalles:
        return None
    if isinstance(venta_con_detalles, list):
        return venta_con_detalles[0] if venta_con_detalles else None
    return venta_con_detalles


async def obtener_detalle_venta_por_venta_id(filtros: dict = None):
    """Conveniencia: wrapper para obtenerDetalleVenta filtrando por id_ventafk."""
    return await obtenerDetalleVenta(filtros=filtros)


async def crear_venta(payload: dict):
    venta = build_venta_entity(payload)
    return await actualizarVenta(venta)


async def actualizar_venta(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarVenta(payload, id)

