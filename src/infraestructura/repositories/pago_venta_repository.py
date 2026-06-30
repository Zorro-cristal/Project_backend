from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update

from ..models.pago_venta import PagoVenta


async def obtenerPagoVenta(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('pagos_venta', filtros, limite, offset, columns=columnas)


async def actualizarPagoVenta(datos: Union[PagoVenta, dict], id: Optional[int] = None):
    if isinstance(datos, PagoVenta):
        payload = {k: v for k, v in datos.__dict__.items() if v is not None}
    else:
        payload = datos
    
    if id is None:
        return await insert('pagos_venta', payload)
    return await update('pagos_venta', id, payload, key='id')


async def obtenerPagosPorVentaId(id_ventafk: int, columnas: str = "*"):
    """Obtiene todos los pagos asociados a una venta."""
    filtros = {'id_ventafk': id_ventafk}
    return await get('pagos_venta', filtros, limite=100, offset=0, columns=columnas, order_by='fecha', order_desc=False)


async def obtenerTotalPagadoPorVentaId(id_ventafk: int) -> float:
    """Calcula el total pagado para una venta específica."""
    pagos = await obtenerPagosPorVentaId(id_ventafk)
    total = 0.0
    for pago in (pagos or []):
        monto = pago.get('monto') or 0
        estado = pago.get('estado') or 1
        # Solo contar pagos activos (estado = 1)
        if estado == 1:
            total += float(monto)
    return total
