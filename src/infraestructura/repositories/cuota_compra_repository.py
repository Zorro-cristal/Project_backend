from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update

from ..models.cuota_compra import CuotaCompra


async def obtenerCuotaCompra(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('cuotas_compra', filtros, limite, offset, columns=columnas)


async def actualizarCuotaCompra(datos: Union[CuotaCompra, dict], id: Optional[int] = None):
    if isinstance(datos, CuotaCompra):
        payload = {k: v for k, v in datos.__dict__.items() if v is not None}
    else:
        payload = datos
    
    if id is None:
        return await insert('cuotas_compra', payload)
    return await update('cuotas_compra', id, payload, key='id')


async def obtenerCuotasPorCompraId(id_comprafk: int, columnas: str = "*"):
    """Obtiene todas las cuotas asociadas a una compra."""
    filtros = {'id_comprafk': id_comprafk}
    return await get('cuotas_compra', filtros, limit=100, offset=0, columns=columnas, order_by='fecha', order_desc=False)
