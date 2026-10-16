from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.proveedor import Proveedor


async def obtenerProveedor(filtros=None, limite=100, offset=0, columnas="*"):
    joins = [{
        "table": "personas",
        "foreign_key": "cedula",
        "primary_key": "cedula",
        "type": "LEFT",
    }]
    return await get(
        'proveedores',
        filtros,
        limite,
        offset,
        columns="*, personas(cedula,nombres, apellidos, telefono)",
        joins=joins,
    )


async def actualizarProveedor(datos: Union[Proveedor, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['persona'])

    if id is None:
        return await insert('proveedores', payload)
    return await update('proveedores', id, payload)
