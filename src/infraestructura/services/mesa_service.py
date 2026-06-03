from ..repositories.mesa_repository import actualizarMesa, obtenerMesa
from ..models.mesa import Mesa
from .local_service import obtener_locales


def build_mesa_entity(payload: dict) -> Mesa:
    valid_fields = {key: value for key, value in payload.items() if key in Mesa.__annotations__}
    return Mesa(**valid_fields)


async def attach_local_data(mesas: list[dict]) -> list[dict]:
    local_ids = {mesa.get('id_localfk') for mesa in mesas if mesa.get('id_localfk')}
    if not local_ids:
        return mesas

    filtros = {'id': list(local_ids)}
    locales = await obtener_locales(filtros)

    local_map = {local['id']: local for local in (locales or [])}
    for mesa in mesas:
        local_id = mesa.get('id_localfk')
        mesa['local'] = local_map.get(local_id)
    return mesas


async def obtener_mesas(filtros: dict = None, columnas: str = '*'):
    mesas = await obtenerMesa(filtros=filtros, columnas=columnas)
    if not mesas:
        return mesas
    return await attach_local_data(mesas)


async def crear_mesa(payload: dict):
    mesa = build_mesa_entity(payload)
    return await actualizarMesa(mesa)


async def actualizar_mesa(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarMesa(payload, id)
