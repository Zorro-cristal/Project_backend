from typing import Optional

from src.infraestructura.repositories.compra_repository import actualizarCompra, obtenerCompra
from src.infraestructura.models.compra import Compra
from src.infraestructura.services.cliente_service import obtener_clientes
from src.infraestructura.services.local_service import obtener_locales
from src.infraestructura.services.proveedor_service import obtener_proveedores
from src.infraestructura.repositories.detalle_compra_repository import obtenerDetalleCompra


def build_compra_entity(payload: dict) -> Compra:
    valid_fields = {key: value for key, value in payload.items() if key in Compra.__annotations__}
    return Compra(**valid_fields)


async def attach_related_data(compras: list[dict]) -> list[dict]:
    cliente_ids = {compra.get('id_clienteFK') for compra in compras if compra.get('id_clienteFK')}
    local_ids = {compra.get('id_localFK') for compra in compras if compra.get('id_localFK')}
    proveedor_ids = {compra.get('id_proveedorFK') for compra in compras if compra.get('id_proveedorFK')}
    compra_ids = {compra.get('id') for compra in compras if compra.get('id')}

    cliente_map = {}
    if cliente_ids:
        clientes = await obtener_clientes({'id': list(cliente_ids)})
        cliente_map = {cliente['id']: cliente for cliente in (clientes or [])}

    local_map = {}
    if local_ids:
        locales = await obtener_locales({'id': list(local_ids)})
        local_map = {local['id']: local for local in (locales or [])}

    proveedor_map = {}
    if proveedor_ids:
        proveedores = await obtener_proveedores({'id': list(proveedor_ids)})
        proveedor_map = {proveedor['id']: proveedor for proveedor in (proveedores or [])}

    detalle_map = {}
    if compra_ids:
        detalles = await obtenerDetalleCompra({'id_compraFK': list(compra_ids)})
        for detalle in (detalles or []):
            compra_id = detalle.get('id_compraFK')
            if compra_id not in detalle_map:
                detalle_map[compra_id] = []
            detalle_map[compra_id].append(detalle)

    for compra in compras:
        compra_id = compra.get('id')
        compra['cliente'] = cliente_map.get(compra.get('id_clienteFK'))
        compra['local'] = local_map.get(compra.get('id_localFK'))
        compra['proveedor'] = proveedor_map.get(compra.get('id_proveedorFK'))
        compra['detalles'] = detalle_map.get(compra_id, [])

    return compras


async def obtener_compras(filtros: dict = None, columnas: str = '*'):
    compras = await obtenerCompra(filtros=filtros, columnas=columnas)
    if not compras:
        return compras
    return await attach_related_data(compras)


async def crear_compra(payload: dict):
    compra = build_compra_entity(payload)
    return await actualizarCompra(compra)


async def actualizar_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarCompra(payload, id)
