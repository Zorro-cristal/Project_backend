from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.venta import Venta


async def obtenerVenta(filtros=None, limite=100, offset=0, columnas="*", joins=None):
    return await get('ventas', filtros, limite, offset, columns=columnas, joins=joins)


async def actualizarVenta(datos: Union[Venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario', 'cliente', 'local', 'caja', 'detalles'])


    if id is None:
        return await insert('ventas', payload)
    return await update('ventas', id, payload, key='id_venta')
