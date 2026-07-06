from typing import Optional, Union

from ..models.stock import Stock
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerStock(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('stocks', filtros, limite, offset, order_by= 'fecha_vencimiento', order_desc= False)


async def actualizarStock(datos: Union[Stock, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['local', 'detalles_producto'])

    if id is None:
        return await insert('stocks', payload)
    return await update('stocks', id, payload)
