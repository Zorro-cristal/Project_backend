from ..repositories.mesa_repository import actualizarMesa, obtenerMesa
from ..models.mesa import Mesa
from .local_service import obtener_locales
from src.shell.utils import attach_related


def build_mesa_entity(payload: dict) -> Mesa:
    valid_fields = {key: value for key, value in payload.items() if key in Mesa.__annotations__}
    return Mesa(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_mesas(filtros: dict = None, columnas: str = '*'):
    mesas = await obtenerMesa(filtros=filtros, columnas=columnas)
    if not mesas:
        return mesas
    return await attach_related(mesas, 'id_localfk', obtener_locales, 'id', 'id', 'local')


async def crear_mesa(payload: dict):
    mesa = build_mesa_entity(payload)
    return await actualizarMesa(mesa)


async def actualizar_mesa(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarMesa(payload, id)
