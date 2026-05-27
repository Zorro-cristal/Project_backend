from typing import Optional, Union

from src.infraestructura.models.venta import Venta
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerVenta(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('ventas', filtros, limite, offset)


async def actualizarVenta(datos: Union[Venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario', 'cliente', 'local', 'detalles'])

    if id is None:
        return await insert('ventas', payload)
    return await update('ventas', id, payload, key='id_venta')
