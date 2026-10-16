from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.mesa import Mesa


async def obtenerMesa(filtros=None, limite=100, offset=0, columnas="*"):
    joins = [{
        "table": "locales",
        "foreign_key": "id_localfk",
        "primary_key": "id",
        "type": "LEFT",
    }]
    return await get(
        'mesas',
        filtros,
        limite,
        offset,
        columns="*, locales(id, nombre, direccion)",
        joins=joins,
    )


async def actualizarMesa(datos: Union[Mesa, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['local'])

    if id is None:
        return await insert('mesas', payload)
    return await update('mesas', id, payload)
