from src.infraestructura.services.local_service import crear_local, actualizar_local


async def crear_o_actualizar_local(payload: dict):
    return await crear_local(payload)


async def actualizar_local_por_id(id_local: int, payload: dict):
    return await actualizar_local(id_local, payload)
