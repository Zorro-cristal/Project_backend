from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update

from ..models.pago_compra import PagoCompra


async def obtenerPagoCompra(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('pagos_compra', filtros, limite, offset, columns=columnas)


async def actualizarPagoCompra(datos: Union[PagoCompra, dict], id: Optional[int] = None):
    if isinstance(datos, PagoCompra):
        payload = {k: v for k, v in datos.__dict__.items() if v is not None}
    else:
        payload = datos
    
    if id is None:
        return await insert('pagos_compra', payload)
    return await update('pagos_compra', id, payload, key='id')


async def obtenerPagosPorCompraId(id_comprafk: int, columnas: str = "*"):
    """Obtiene todos los pagos asociados a una compra."""
    filtros = {'id_comprafk': id_comprafk}
    return await get('pagos_compra', filtros, limite=100, offset=0, columns=columnas, order_by='fecha', order_desc=False)


async def obtenerTotalPagadoPorCompraId(id_comprafk: int) -> float:
    """Calcula el total pagado para una compra específica."""
    pagos = await obtenerPagosPorCompraId(id_comprafk)
    total = 0.0
    for pago in (pagos or []):
        monto = pago.get('monto') or 0
        estado = pago.get('estado') or 1
        # Solo contar pagos activos (estado = 1)
        if estado == 1:
            total += float(monto)
    return total
