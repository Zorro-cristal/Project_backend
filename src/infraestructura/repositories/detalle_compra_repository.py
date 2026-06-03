from typing import Optional, Union

from ..models.detalle_compra import Detalle_compra
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerDetalleCompra(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('detalle_compra', filters=filtros, limit=limite, offset=offset)


async def actualizarDetalleCompra(datos: Union[Detalle_compra, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['producto', 'compra'])

    if id is None:
        return await insert('detalle_compra', payload)
    return await update('detalle_compra', id, payload, key='id_detalle_compra')
