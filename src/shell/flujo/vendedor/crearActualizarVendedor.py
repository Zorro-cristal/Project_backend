from src.infraestructura.services.vendedor_service import crear_vendedor, actualizar_vendedor
from src.shell.flujo.persona.crearActualizarPersona import crear_o_actualizar_persona


async def crear_o_actualizar_vendedor(payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personaFK'] = persona.get('cedula')

    return await crear_vendedor(payload)


async def actualizar_vendedor_por_id(id_vendedor: int, payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personaFK'] = persona.get('cedula')

    return await actualizar_vendedor(id_vendedor, payload)
