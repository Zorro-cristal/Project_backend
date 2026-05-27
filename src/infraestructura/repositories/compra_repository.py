from typing import Optional, Union

from src.infraestructura.models.compra import Compra
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerCompra(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('compras', filtros, limite, offset)


async def actualizarCompra(datos: Union[Compra, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['local', 'cliente', 'proveedor', 'detalles'])

    if id is None:
        return await insert('compras', payload)
    return await update('compras', id, payload, key='id_compra')
