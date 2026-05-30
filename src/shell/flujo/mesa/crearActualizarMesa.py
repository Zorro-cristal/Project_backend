from src.infraestructura.services.mesa_service import crear_mesa, actualizar_mesa
from src.shell.flujo.local.crearActualizarLocal import crear_o_actualizar_local


async def crear_o_actualizar_mesa(payload: dict):
    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_o_actualizar_local(local_payload)
        payload['id_localfk'] = local.get('id')

    return await crear_mesa(payload)


async def actualizar_mesa_por_id(id_mesa: int, payload: dict):
    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_o_actualizar_local(local_payload)
        payload['id_localfk'] = local.get('id')

    return await actualizar_mesa(id_mesa, payload)
