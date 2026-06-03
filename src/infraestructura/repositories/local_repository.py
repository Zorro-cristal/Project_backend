from typing import Optional, Union

from ..models.local import Local
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerLocal(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('locales', filtros, limite, offset)


async def actualizarLocal(datos: Union[Local, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=[])

    if id is None:
        return await insert('locales', payload)
    return await update('locales', id, payload)
