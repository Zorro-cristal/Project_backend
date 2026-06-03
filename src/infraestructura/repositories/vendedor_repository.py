from typing import Optional, Union

from ..models.vendedor import Vendedor
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerVendedor(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('vendedores', filtros, limite, offset)


async def actualizarVendedor(datos: Union[Vendedor, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['persona'])

    if id is None:
        return await insert('vendedores', payload)
    return await update('vendedores', id, payload)
