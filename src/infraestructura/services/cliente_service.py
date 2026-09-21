from src.shell.utils import attach_related, filtrar_por_nombre_completo

from ..models.cliente import Cliente
from ..repositories.cliente_repository import actualizarCliente, obtenerCliente
from .persona_service import (actualizar_persona, crear_persona,
                              obtener_personas)


def build_cliente_entity(payload: dict) -> Cliente:
    valid_fields = {key: value for key, value in payload.items() if key in Cliente.__annotations__}
    return Cliente(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_clientes(filtros: dict= None, columnas: str = '*', limite: int = 100, offset: int = 0):
    filtros = dict(filtros or {})
    nombre_completo = filtros.pop("nombre_completo", None)
    clientes = await obtenerCliente(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    return clientes


async def crear_cliente(payload: dict):
    cliente = build_cliente_entity(payload)
    return await actualizarCliente(cliente)


async def actualizar_cliente(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarCliente(payload, id)
