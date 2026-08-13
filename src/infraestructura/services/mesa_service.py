from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.mesa import Mesa
from ..repositories.mesa_repository import actualizarMesa, obtenerMesa
from ..repositories.orden_repository import obtenerOrdenes
from .cliente_service import obtener_clientes
from .local_service import obtener_locales


def build_mesa_entity(payload: dict) -> Mesa:
    valid_fields = {key: value for key, value in payload.items() if key in Mesa.__annotations__}
    return Mesa(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_mesas(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    mesas = await obtenerMesa(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    if not mesas:
        return mesas

    mesas = await attach_related(mesas, 'id_clientefk', obtener_clientes, 'id', 'id', 'cliente')
    mesas = await attach_grouped(
        mesas,
        parent_id_field='id',
        fetch_func=obtenerOrdenes,
        fetch_filter_name='id_mesafk',
        child_parent_field='id_mesafk',
        output_field='ordenes',
    )
    return mesas


async def crear_mesa(payload: dict):
    await validar_fk_existente(
        payload.get('id_localfk'),
        obtener_locales,
        'id',
        f"Local con ID {payload.get('id_localfk')} no existe",
    )
    mesa = build_mesa_entity(payload)
    return await actualizarMesa(mesa)


async def actualizar_mesa(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    await validar_fk_existente(
        payload.get('id_localfk'),
        obtener_locales,
        'id',
        f"Local con ID {payload.get('id_localfk')} no existe",
    )
    # Validar id_clientefk si está presente
    if payload.get('id_clientefk') is not None:
        await validar_fk_existente(
            payload.get('id_clientefk'),
            obtener_clientes,
            'id',
            f"Cliente con ID {payload.get('id_clientefk')} no existe",
        )
    return await actualizarMesa(payload, id)
