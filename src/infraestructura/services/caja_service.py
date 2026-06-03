from src.shell.utils import attach_related, validar_fk_existente

from ..models.caja import Caja
from ..repositories.caja_repository import actualizarCaja, obtenerCaja
from .usuario_service import obtener_usuarios


def build_caja_entity(payload: dict) -> Caja:
    valid_fields = {key: value for key, value in payload.items() if key in Caja.__annotations__}
    return Caja(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_cajas(filtros: dict = None, columnas: str = '*'):
    cajas = await obtenerCaja(filtros=filtros, columnas=columnas)
    if not cajas:
        return cajas
    return await attach_related(cajas, 'id_usuariofk', obtener_usuarios, 'id', 'id', 'usuario')


async def crear_caja(payload: dict):
    await validar_fk_existente(
        payload.get('id_usuariofk'),
        obtener_usuarios,
        'id',
        f"Usuario con ID {payload.get('id_usuariofk')} no existe",
    )
    caja = build_caja_entity(payload)
    return await actualizarCaja(caja)


async def actualizar_caja(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    await validar_fk_existente(
        payload.get('id_usuariofk'),
        obtener_usuarios,
        'id',
        f"Usuario con ID {payload.get('id_usuariofk')} no existe",
    )
    return await actualizarCaja(payload, id)
