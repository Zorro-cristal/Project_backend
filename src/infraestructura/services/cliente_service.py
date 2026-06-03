from ..repositories.cliente_repository import actualizarCliente, obtenerCliente
from ..models.cliente import Cliente
from .persona_service import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)
from src.shell.utils import attach_related


def build_cliente_entity(payload: dict) -> Cliente:
    valid_fields = {key: value for key, value in payload.items() if key in Cliente.__annotations__}
    return Cliente(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_clientes(filtros: dict= None, columnas: str = '*'):
    clientes = await obtenerCliente(filtros=filtros, columnas=columnas)
    if not clientes:
        return clientes
    return await attach_related(clientes, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'persona')


async def crear_cliente(payload: dict):
    cliente = build_cliente_entity(payload)
    return await actualizarCliente(cliente)


async def actualizar_cliente(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarCliente(payload, id)
