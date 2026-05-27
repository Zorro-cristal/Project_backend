from typing import Optional, Union

from src.infraestructura.models.detalle_producto import Detalle_producto
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerDetalleProducto(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('detalles_producto', filtros, limite, offset)

async def actualizarDetalleProducto(datos: Union[Detalle_producto, dict], cod_barra: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if cod_barra is None:
        return await insert('detalles_producto', payload)
    return await update('detalles_producto', cod_barra, payload, key='cod_barra')
