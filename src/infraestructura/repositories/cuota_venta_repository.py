from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update

from ..models.cuota_venta import CuotaVenta


async def obtenerCuotaVenta(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('cuotas_venta', filtros, limite, offset, columns=columnas)


async def actualizarCuotaVenta(datos: Union[CuotaVenta, dict], id: Optional[int] = None):
    if isinstance(datos, CuotaVenta):
        payload = {k: v for k, v in datos.__dict__.items() if v is not None}
    else:
        payload = datos
    
    if id is None:
        return await insert('cuotas_venta', payload)
    return await update('cuotas_venta', id, payload, key='id')


async def obtenerCuotasPorVentaId(id_ventafk: int, columnas: str = "*"):
    """Obtiene todas las cuotas asociadas a una venta."""
    filtros = {'id_ventafk': id_ventafk}
    return await get('cuotas_venta', filtros, limit=100, offset=0, columns=columnas, order_by='fecha', order_desc=False)
