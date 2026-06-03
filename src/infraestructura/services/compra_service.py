from typing import Optional

from src.shell.utils import attach_grouped, attach_related

from ..models.compra import Compra
from ..repositories.compra_repository import actualizarCompra, obtenerCompra
from ..repositories.detalle_compra_repository import obtenerDetalleCompra
from .cliente_service import obtener_clientes
from .local_service import obtener_locales
from .proveedor_service import obtener_proveedores


def build_compra_entity(payload: dict) -> Compra:
    valid_fields = {key: value for key, value in payload.items() if key in Compra.__annotations__}
    return Compra(**valid_fields)


async def attach_related_data(compras: list[dict]) -> list[dict]:
    # One-to-one attachments
    compras = await attach_related(compras, 'id_clientefk', obtener_clientes, 'id', 'id', 'cliente')
    compras = await attach_related(compras, 'id_localfk', obtener_locales, 'id', 'id', 'local')
    compras = await attach_related(compras, 'id_proveedorfk', obtener_proveedores, 'id', 'id', 'proveedor')
    # One-to-many: detalles por compra id
    compras = await attach_grouped(compras, 'id', obtenerDetalleCompra, 'id_comprafk', 'id_comprafk', 'detalles')
    return compras


async def obtener_compras(filtros: dict = None, columnas: str = '*'):
    """Obtiene compras e incluye datos relacionados (incluye detalles)."""
    compras = await obtenerCompra(filtros=filtros, columnas=columnas)
    if not compras:
        return compras
    return await attach_related_data(compras)


async def obtener_compra_solo(id: int):
    """Obtiene una compra sin adjuntar detalles (detalle_compra)."""
    compras = await obtenerCompra(filtros={"id": id}, columnas='*')
    if not compras:
        return compras

    compra = compras[0] if isinstance(compras, list) else compras
    # Mantener relaciones básicas (cliente/local/proveedor) sin detalles
    cliente_id = compra.get('id_clientefk')
    local_id = compra.get('id_localfk')
    proveedor_id = compra.get('id_proveedorfk')

    # Cargar relaciones si existen
    compra['cliente'] = None
    compra['local'] = None
    compra['proveedor'] = None

    if cliente_id:
        clientes = await obtener_clientes({'id': [cliente_id]})
        compra['cliente'] = (clientes or [None])[0] if clientes else None

    if local_id:
        locales = await obtener_locales({'id': [local_id]})
        compra['local'] = (locales or [None])[0] if locales else None

    if proveedor_id:
        proveedores = await obtener_proveedores({'id': [proveedor_id]})
        compra['proveedor'] = (proveedores or [None])[0] if proveedores else None

    return compra


async def obtener_compra_con_detalles(id: int, solo_detalles: bool = False):
    """Obtiene compra con sus detalle_compra. Si solo_detalles=True, devuelve solo detalles."""
    compras = await obtener_compras(filtros={"id": id})
    if not compras:
        return compras

    compra = compras[0] if isinstance(compras, list) else compras
    if solo_detalles:
        return compra.get('detalles', [])
    return compra



async def crear_compra(payload: dict):
    compra = build_compra_entity(payload)
    return await actualizarCompra(compra)


async def actualizar_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarCompra(payload, id)
