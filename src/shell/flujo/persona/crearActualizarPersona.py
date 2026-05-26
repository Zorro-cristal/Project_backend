from src.infraestructura.services.persona_service import crear_persona, obtener_personas, actualizar_persona

async def crear_o_actualizar_persona(payload: dict):
    cedula = payload.get('cedula')
    if cedula is not None:
        existentes = await obtener_personas({'cedula': cedula})
        if existentes and len(existentes) > 0:
            return await actualizar_persona(cedula, payload)

    return await crear_persona(payload)
