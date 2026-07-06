from src.infraestructura.services.vendedor_service import crear_vendedor, actualizar_vendedor


async def crear_o_actualizar_vendedor(payload: dict):
    # El vendedor ahora se vincula a usuarios (id_usuariofk), no a persona.
    payload.pop('persona', None)
    return await crear_vendedor(payload)


async def actualizar_vendedor_por_id(id_vendedor: int, payload: dict):
    # El vendedor ahora se vincula a usuarios (id_usuariofk), no a persona.
    payload.pop('persona', None)
    return await actualizar_vendedor(id_vendedor, payload)
