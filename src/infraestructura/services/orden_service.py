from typing import Optional

from ..models.orden import Orden
from ..repositories.orden_repository import actualizarOrden, obtenerOrdenes
from ..repositories.precio_repository import obtenerPrecio
from .mesa_service import obtener_mesas


def build_orden_entity(payload: dict) -> Orden:
    valid_fields = {key: value for key, value in payload.items() if key in Orden.__annotations__}
    return Orden(**valid_fields)


async def obtener_ordenes(filtros: dict = None, columnas: str = '*'):
    ordenes = await obtenerOrdenes(filtros=filtros, columnas=columnas)
    if not ordenes:
        return ordenes
    return await attach_related_data(ordenes)


async def obtener_orden_por_id(filtros: dict = None, columnas: str = '*'):
    ordenes = await obtenerOrdenes(filtros=filtros, columnas=columnas)
    if not ordenes:
        return None
    if isinstance(ordenes, list):
        orden = ordenes[0] if ordenes else None
    else:
        orden = ordenes
    if not orden:
        return None
    return await attach_related_data([orden])


async def attach_related_data(ordenes: list[dict]) -> list[dict]:
    # Attach mesa data
    mesa_ids = {o.get('id_mesafk') for o in ordenes if o.get('id_mesafk')}
    if mesa_ids:
        mesas = await obtener_mesas({'id': list(mesa_ids)})
        mesa_map = {m['id']: m for m in (mesas or [])}
        for o in ordenes:
            o['mesa'] = mesa_map.get(o.get('id_mesafk'))
    else:
        for o in ordenes:
            o['mesa'] = None

    # Attach precio data
    precio_ids = {o.get('id_preciofk') for o in ordenes if o.get('id_preciofk')}
    if precio_ids:
        precios = await obtenerPrecio({'id': list(precio_ids)})
        precio_map = {p['id']: p for p in (precios or [])}
        for o in ordenes:
            o['precio'] = precio_map.get(o.get('id_preciofk'))
    else:
        for o in ordenes:
            o['precio'] = None

    return ordenes


async def crear_orden(payload: dict):
    orden = build_orden_entity(payload)
    return await actualizarOrden(orden)


async def actualizar_orden_por_id(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarOrden(payload, id)

