from src.infraestructura.services.proveedor_service import crear_proveedor, actualizar_proveedor
from src.shell.flujo.persona.crearActualizarPersona import crear_o_actualizar_persona


async def crear_o_actualizar_proveedor(payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personaFK'] = persona.get('cedula')

    return await crear_proveedor(payload)


async def actualizar_proveedor_por_id(id_proveedor: int, payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personaFK'] = persona.get('cedula')

    return await actualizar_proveedor(id_proveedor, payload)
