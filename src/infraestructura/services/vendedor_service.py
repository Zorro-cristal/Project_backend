from ..repositories.vendedor_repository import actualizarVendedor, obtenerVendedor
from ..models.vendedor import Vendedor
from .persona_service import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)
from src.shell.utils import attach_related


def build_vendedor_entity(payload: dict) -> Vendedor:
    valid_fields = {key: value for key, value in payload.items() if key in Vendedor.__annotations__}
    return Vendedor(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_vendedores(filtros: dict = None, columnas: str = '*'):
    vendedores = await obtenerVendedor(filtros=filtros, columnas=columnas)
    if not vendedores:
        return vendedores
    return await attach_related(vendedores, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'persona')


async def crear_vendedor(payload: dict):
    vendedor = build_vendedor_entity(payload)
    return await actualizarVendedor(vendedor)


async def actualizar_vendedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarVendedor(payload, id)
