from ..repositories.caja_repository import actualizarCaja, obtenerCaja
from ..models.caja import Caja
from .usuario_service import obtener_usuarios


def build_caja_entity(payload: dict) -> Caja:
    valid_fields = {key: value for key, value in payload.items() if key in Caja.__annotations__}
    return Caja(**valid_fields)


async def attach_usuario_data(cajas: list[dict]) -> list[dict]:
    usuario_ids = {caja.get('id_usuariofk') for caja in cajas if caja.get('id_usuariofk')}
    if not usuario_ids:
        return cajas

    filtros = {'id': list(usuario_ids)}
    usuarios = await obtener_usuarios(filtros)

    usuario_map = {usuario['id']: usuario for usuario in (usuarios or [])}
    for caja in cajas:
        usuario_id = caja.get('id_usuariofk')
        caja['usuario'] = usuario_map.get(usuario_id)
    return cajas


async def obtener_cajas(filtros: dict = None, columnas: str = '*'):
    cajas = await obtenerCaja(filtros=filtros, columnas=columnas)
    if not cajas:
        return cajas
    return await attach_usuario_data(cajas)


async def crear_caja(payload: dict):
    caja = build_caja_entity(payload)
    return await actualizarCaja(caja)


async def actualizar_caja(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarCaja(payload, id)
