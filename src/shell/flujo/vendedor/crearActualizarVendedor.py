from src.infraestructura.services.vendedor_service import (actualizar_vendedor,
                                                           crear_vendedor)


async def crear_o_actualizar_vendedor(payload: dict):
    # El vendedor ahora se vincula a usuarios (id_usuariofk), no a persona.
    payload.pop('personas', None)
    return await crear_vendedor(payload)


async def actualizar_vendedor_por_id(id_vendedor: int, payload: dict):
    # El vendedor ahora se vincula a usuarios (id_usuariofk), no a persona.
    payload.pop('personas', None)
    return await actualizar_vendedor(id_vendedor, payload)
