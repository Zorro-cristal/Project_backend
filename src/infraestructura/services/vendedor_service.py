from ..repositories.vendedor_repository import actualizarVendedor, obtenerVendedor
from ..models.vendedor import Vendedor
from .persona_service import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)


def build_vendedor_entity(payload: dict) -> Vendedor:
    valid_fields = {key: value for key, value in payload.items() if key in Vendedor.__annotations__}
    return Vendedor(**valid_fields)


async def attach_persona_data(vendedores: list[dict]) -> list[dict]:
    persona_ids = {vendedor.get('id_personafk') for vendedor in vendedores if vendedor.get('id_personafk')}
    if not persona_ids:
        return vendedores

    filtros = {'cedula': list(persona_ids)}
    personas = await obtener_personas(filtros)

    persona_map = {persona['cedula']: persona for persona in (personas or [])}
    for vendedor in vendedores:
        persona_id = vendedor.get('id_personafk')
        vendedor['persona'] = persona_map.get(persona_id)
    return vendedores


async def obtener_vendedores(filtros: dict = None, columnas: str = '*'):
    vendedores = await obtenerVendedor(filtros=filtros, columnas=columnas)
    if not vendedores:
        return vendedores
    return await attach_persona_data(vendedores)


async def crear_vendedor(payload: dict):
    vendedor = build_vendedor_entity(payload)
    return await actualizarVendedor(vendedor)


async def actualizar_vendedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarVendedor(payload, id)
