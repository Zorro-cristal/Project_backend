from src.shell.utils import attach_related, validar_fk_existente

from ..models.egreso import Egreso
from ..repositories.egreso_repository import actualizarEgreso, obtenerEgreso
from .caja_service import obtener_cajas


def build_egreso_entity(payload: dict) -> Egreso:
    valid_fields = {key: value for key, value in payload.items() if key in Egreso.__annotations__}
    return Egreso(**valid_fields)


async def obtener_egresos(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    egresos = await obtenerEgreso(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    if not egresos:
        return egresos
    return await attach_related(egresos, 'id_cajafk', obtener_cajas, 'id', 'id', 'caja')


async def obtener_egreso_por_id(filtros: dict = None, columnas: str = '*'):
    egreso = await obtenerEgreso(filtros=filtros, columnas=columnas)
    if not egreso:
        return None
    if isinstance(egreso, list):
        return egreso[0] if egreso else None
    return egreso


async def obtener_egreso_por_id_con_caja(filtros: dict = None, columnas: str = '*'):
    egreso_con_caja = await obtener_egresos(filtros=filtros, columnas=columnas)
    if not egreso_con_caja:
        return None
    if isinstance(egreso_con_caja, list):
        return egreso_con_caja[0] if egreso_con_caja else None
    return egreso_con_caja


async def crear_egreso(payload: dict):
    await validar_fk_existente(
        payload.get('id_cajafk'),
        obtener_cajas,
        'id',
        f"Caja con ID {payload.get('id_cajafk')} no existe",
    )
    egreso = build_egreso_entity(payload)
    return await actualizarEgreso(egreso)


async def actualizar_egreso(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    await validar_fk_existente(
        payload.get('id_cajafk'),
        obtener_cajas,
        'id',
        f"Caja con ID {payload.get('id_cajafk')} no existe",
    )
    return await actualizarEgreso(payload, id)
