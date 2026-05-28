from typing import Optional, Union

from src.infraestructura.models.detalle_venta import Detalle_venta
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerDetalleVenta(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('detalle_venta', filters=filtros, limit=limite, offset=offset)


async def actualizarDetalleVenta(datos: Union[Detalle_venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['producto', 'venta'])

    if id is None:
        return await insert('detalle_venta', payload)
    return await update('detalle_venta', id, payload, key='id_detalle_venta')
