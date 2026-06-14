from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.egreso import Egreso


async def obtenerEgreso(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('egresos', filtros, limite, offset, columns=columnas)


async def actualizarEgreso(datos: Union[Egreso, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['caja'])

    if id is None:
        return await insert('egresos', payload)
    return await update('egresos', id, payload)
