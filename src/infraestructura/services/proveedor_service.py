from ..repositories.proveedor_repository import actualizarProveedor, obtenerProveedor
from ..models.proveedor import Proveedor
from .persona_service import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)


def build_proveedor_entity(payload: dict) -> Proveedor:
    valid_fields = {key: value for key, value in payload.items() if key in Proveedor.__annotations__}
    return Proveedor(**valid_fields)


async def attach_persona_data(proveedores: list[dict]) -> list[dict]:
    persona_ids = {proveedor.get('id_personafk') for proveedor in proveedores if proveedor.get('id_personafk')}
    if not persona_ids:
        return proveedores

    filtros = {'cedula': list(persona_ids)}
    personas = await obtener_personas(filtros)

    persona_map = {persona['cedula']: persona for persona in (personas or [])}
    for proveedor in proveedores:
        persona_id = proveedor.get('id_personafk')
        proveedor['persona'] = persona_map.get(persona_id)
    return proveedores


async def obtener_proveedores(filtros: dict = None, columnas: str = '*'):
    proveedores = await obtenerProveedor(filtros=filtros, columnas=columnas)
    if not proveedores:
        return proveedores
    return await attach_persona_data(proveedores)


async def crear_proveedor(payload: dict):
    proveedor = build_proveedor_entity(payload)
    return await actualizarProveedor(proveedor)


async def actualizar_proveedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarProveedor(payload, id)
