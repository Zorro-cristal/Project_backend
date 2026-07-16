from typing import Optional, Union

from ..models.caja import Caja
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerCaja(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('cajas', filtros, limite, offset, order_by='fecha_cierre')


async def actualizarCaja(datos: Union[Caja, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario'])

    if id is None:
        return await insert('cajas', payload)
    return await update('cajas', id, payload)
