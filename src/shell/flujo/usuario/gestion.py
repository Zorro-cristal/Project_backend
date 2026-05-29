from src.infraestructura.services.usuario_service import (actualizar_usuario,
                                                          crear_usuario,
                                                          obtenerUsuarios)
from src.shell.flujo.persona.crearActualizarPersona import \
    crear_o_actualizar_persona


async def crear_o_actualizar_usuario(payload: dict):
    alias = payload.get('alias')
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personafk'] = persona.get('cedula')

    if alias is not None:
        existentes = await obtenerUsuarios({'alias': alias}, 1, 0)
        if existentes and len(existentes) > 0:
            usuario_existente = existentes[0]
            return await actualizar_usuario(usuario_existente.get('id'), payload)

    return await crear_usuario(payload)


async def actualizar_usuario_por_id(id_usuario: int, payload: dict):
    persona_payload = payload.pop('persona', None)
    if persona_payload is not None:
        persona = await crear_o_actualizar_persona(persona_payload)
        payload['id_personafk'] = persona.get('cedula')

    return await actualizar_usuario(id_usuario, payload)
