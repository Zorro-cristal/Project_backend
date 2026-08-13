from typing import Optional

from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.caja import Caja
from ..repositories.caja_repository import actualizarCaja, obtenerCaja
from ..repositories.egreso_repository import obtenerEgreso
from ..repositories.pago_compra_repository import obtenerPagoCompra
from ..repositories.pago_venta_repository import obtenerPagoVenta
from .usuario_service import obtener_usuarios_sin_rol


def build_caja_entity(payload: dict) -> Caja:
    valid_fields = {key: value for key, value in payload.items() if key in Caja.__annotations__}
    return Caja(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_cajas(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    cajas = await obtenerCaja(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    if not cajas:
        return cajas
    # En endpoints GET adjuntamos `usuario` sin `rol`
    return await attach_related(cajas, 'id_usuariofk', obtener_usuarios_sin_rol, 'id', 'id', 'usuario')


async def obtener_caja_id_usuario(filtros: dict = None, id_cajafk: int | None = None) -> Optional[int]:
    """
    Obtiene SOLO el id_usuariofk de una caja, sin adjuntar usuario/persona/rol.

    Esto evita errores de "Usuario no encontrado" cuando el join/adjunto falla
    pero el flujo de compra necesita únicamente el FK.
    """
    if id_cajafk is not None:
        filtros = {'id': id_cajafk}

    if not filtros:
        return None

    cajas = await obtenerCaja(filtros=filtros, columnas='id_usuariofk')
    if isinstance(cajas, list):
        caja = cajas[0] if cajas else None
    else:
        caja = cajas

    if not caja:
        return None

    return caja.get('id_usuariofk')


async def crear_caja(payload: dict):
    await validar_fk_existente(
        payload.get('id_usuariofk'),
        obtener_usuarios_sin_rol,
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
        obtener_usuarios_sin_rol,
        'id',
        f"Usuario con ID {payload.get('id_usuariofk')} no existe",
    )
    return await actualizarCaja(payload, id)


async def obtener_caja_por_id_con_movimientos(filtros: dict = None, columnas: str = '*'):
    """Retorna la caja por id con movimientos (egresos, pagos_venta, pagos_cuota)."""
    caja = await obtenerCaja(filtros=filtros, columnas=columnas)
    if not caja:
        return None
    
    # El repository devuelve una lista, obtengo el primer elemento
    if isinstance(caja, list):
        caja = caja[0] if caja else None
    
    if not caja:
        return None
    
    caja_id = caja.get('id')
    if caja_id is None:
        return caja
    
    # Convertir a lista para usar attach_grouped
    cajas_list = [caja]
    
    # Adjuntar egresos (filtrar por id_cajafk)
    cajas_list = await attach_grouped(
        cajas_list, 'id', obtenerEgreso, 'id_cajafk', 'id_cajafk', 'egresos'
    )
    
    # Adjuntar pagos de venta (filtrar por id_cajafk)
    cajas_list = await attach_grouped(
        cajas_list, 'id', obtenerPagoVenta, 'id_cajafk', 'id_cajafk', 'pagos_venta'
    )
    
    # Adjuntar pagos de compra (filtrar por id_cajafk)
    cajas_list = await attach_grouped(
        cajas_list, 'id', obtenerPagoCompra, 'id_cajafk', 'id_cajafk', 'pagos_cuota'
    )

    # Adjuntar usuario (persona/rol) asociado a la caja, pero SIN `rol`
    cajas_list = await attach_related(
        cajas_list,
        'id_usuariofk',
        obtener_usuarios_sin_rol,
        'id',
        'id',
        'usuario',
    )

    return cajas_list[0]
