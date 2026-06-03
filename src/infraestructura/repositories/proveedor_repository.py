from typing import Optional, Union

from ..models.proveedor import Proveedor
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerProveedor(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('proveedores', filtros, limite, offset)


async def actualizarProveedor(datos: Union[Proveedor, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['persona'])

    if id is None:
        return await insert('proveedores', payload)
    return await update('proveedores', id, payload)
