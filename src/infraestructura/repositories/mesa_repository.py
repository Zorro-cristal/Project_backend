from typing import Optional, Union

from ..models.mesa import Mesa
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerMesa(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('mesas', filtros, limite, offset)


async def actualizarMesa(datos: Union[Mesa, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['local'])

    if id is None:
        return await insert('mesas', payload)
    return await update('mesas', id, payload)
