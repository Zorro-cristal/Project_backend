from typing import Optional

from ..models.orden import Orden
from ..repositories.orden_repository import actualizarOrden, obtenerOrdenes
from ..repositories.precio_repository import obtenerPrecio
from .detalles_producto_service import obtener_detalles_productos
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

    # Attach detalle_producto data with parent producto
    detalle_producto_ids = {o.get('id_detalleproductofk') for o in ordenes if o.get('id_detalleproductofk')}
    if detalle_producto_ids:
        # Include producto to get the parent producto info
        detalles_producto = await obtener_detalles_productos(
            {'cod_barra': list(detalle_producto_ids)},
            include_producto=True
        )
        detalle_producto_map = {d['cod_barra']: d for d in (detalles_producto or [])}
        for o in ordenes:
            detalle = detalle_producto_map.get(o.get('id_detalleproductofk'))
            # Save the id_productofk before it gets replaced by the producto object
            if detalle and 'id_productofk' in detalle and isinstance(detalle['id_productofk'], dict):
                original_id_productofk = detalle['id_productofk'].get('id')
                # Add producto nested inside detalle_producto
                detalle['producto'] = detalle['id_productofk']
                # Restore the original id_productofk with just the integer
                detalle['id_productofk'] = original_id_productofk
            o['detalle_producto'] = detalle
    else:
        for o in ordenes:
            o['detalle_producto'] = None

    return ordenes


async def crear_orden(payload: dict):
    orden = build_orden_entity(payload)
    return await actualizarOrden(orden)


async def actualizar_orden_por_id(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarOrden(payload, id)
