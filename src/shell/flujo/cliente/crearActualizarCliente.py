from src.infraestructura.services.cliente_service import crear_cliente, actualizar_cliente
from src.shell.flujo.persona.crearActualizarPersona import crear_o_actualizar_persona

async def crear_o_actualizar_cliente(payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personafk'] = persona.get('cedula')

    return await crear_cliente(payload)


async def actualizar_cliente_por_id(id_cliente: int, payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personafk'] = persona.get('cedula')

    return await actualizar_cliente(id_cliente, payload)
