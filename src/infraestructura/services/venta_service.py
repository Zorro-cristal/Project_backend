from typing import Optional

from src.infraestructura.models.venta import Venta
from src.infraestructura.repositories.detalle_venta_repository import \
    obtenerDetalleVenta
from src.infraestructura.repositories.venta_repository import (actualizarVenta,
                                                               obtenerVenta)
from src.infraestructura.services.cliente_service import obtener_clientes
from src.infraestructura.services.local_service import obtener_locales
from src.infraestructura.services.usuario_service import obtener_usuarios


def build_venta_entity(payload: dict) -> Venta:
    valid_fields = {key: value for key, value in payload.items() if key in Venta.__annotations__}
    return Venta(**valid_fields)


async def attach_related_data(ventas: list[dict]) -> list[dict]:
    usuario_ids = {venta.get('id_usuarioFK') for venta in ventas if venta.get('id_usuarioFK')}
    cliente_ids = {venta.get('id_clienteFK') for venta in ventas if venta.get('id_clienteFK')}
    local_ids = {venta.get('id_localFK') for venta in ventas if venta.get('id_localFK')}
    venta_ids = {venta.get('id') for venta in ventas if venta.get('id')}

    usuario_map = {}
    if usuario_ids:
        usuarios = await obtener_usuarios({'id': list(usuario_ids)})
        usuario_map = {usuario['id']: usuario for usuario in (usuarios or [])}

    cliente_map = {}
    if cliente_ids:
        clientes = await obtener_clientes({'id': list(cliente_ids)})
        cliente_map = {cliente['id']: cliente for cliente in (clientes or [])}

    local_map = {}
    if local_ids:
        locales = await obtener_locales({'id': list(local_ids)})
        local_map = {local['id']: local for local in (locales or [])}

    detalle_map = {}
    if venta_ids:
        detalles = await obtenerDetalleVenta({'id_ventaFK': list(venta_ids)})
        for detalle in (detalles or []):
            venta_id = detalle.get('id_ventaFK')
            if venta_id not in detalle_map:
                detalle_map[venta_id] = []
            detalle_map[venta_id].append(detalle)

    for venta in ventas:
        venta_id = venta.get('id')
        venta['usuario'] = usuario_map.get(venta.get('id_usuarioFK'))
        venta['cliente'] = cliente_map.get(venta.get('id_clienteFK'))
        venta['local'] = local_map.get(venta.get('id_localFK'))
        venta['detalles'] = detalle_map.get(venta_id, [])

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
    """Conveniencia: wrapper para obtenerDetalleVenta filtrando por id_ventaFK."""
    return await obtenerDetalleVenta(filtros=filtros)


async def crear_venta(payload: dict):
    venta = build_venta_entity(payload)
    return await actualizarVenta(venta)


async def actualizar_venta(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarVenta(payload, id)

