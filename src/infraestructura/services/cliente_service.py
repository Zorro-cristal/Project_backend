from src.infraestructura.repositories.cliente_repository import actualizarCliente, obtenerCliente
from src.infraestructura.models.cliente import Cliente
from src.infraestructura.services.persona_service import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)


def build_cliente_entity(payload: dict) -> Cliente:
    valid_fields = {key: value for key, value in payload.items() if key in Cliente.__annotations__}
    return Cliente(**valid_fields)


async def attach_persona_data(clientes: list[dict]) -> list[dict]:
    persona_ids = {cliente.get('id_personaFK') for cliente in clientes if cliente.get('id_personaFK')}
    if not persona_ids:
        return clientes

    filtros = {'cedula': list(persona_ids)}
    personas = await obtener_personas(filtros)

    persona_map = {persona['cedula']: persona for persona in (personas or [])}
    for cliente in clientes:
        persona_id = cliente.get('id_personaFK')
        cliente['persona'] = persona_map.get(persona_id)
    return clientes


async def obtener_clientes(filtros: dict= None, columnas: str = '*'):
    clientes = await obtenerCliente(filtros=filtros, columnas=columnas)
    if not clientes:
        return clientes
    return await attach_persona_data(clientes)


async def crear_cliente(payload: dict):
    cliente = build_cliente_entity(payload)
    return await actualizarCliente(cliente)


async def actualizar_cliente(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarCliente(payload, id)
