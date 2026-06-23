from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.caja import Caja
from ..repositories.caja_repository import actualizarCaja, obtenerCaja
from ..repositories.compra_repository import obtenerCompra
from ..repositories.egreso_repository import obtenerEgreso
from ..repositories.venta_repository import obtenerVenta
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


async def obtener_caja_por_id_con_movimientos(filtros: dict = None, columnas: str = '*'):
    """Retorna la caja por id con movimientos (egresos, ventas, compras)."""
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
    
    # Adjuntar ventas (filtrar por id_cajafk)
    cajas_list = await attach_grouped(
        cajas_list, 'id', obtenerVenta, 'id_cajafk', 'id_cajafk', 'ventas'
    )
    
    # Adjuntar compras (filtrar por id_cajafk)
    cajas_list = await attach_grouped(
        cajas_list, 'id', obtenerCompra, 'id_cajafk', 'id_cajafk', 'compras'
    )
    
    return cajas_list[0]
