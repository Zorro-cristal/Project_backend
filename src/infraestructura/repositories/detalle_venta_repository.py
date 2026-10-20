from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.detalle_venta import Detalle_venta


async def obtenerDetalleVenta(filtros=None, limite=100, offset=0, columnas="*"):
    proyeccion = columnas
    if "detalles_producto" not in proyeccion.lower():
        proyeccion = f"{proyeccion}, detalles_producto(*, productos(*))"

    detalles = await get(
        'detalle_venta',
        filters=filtros,
        limit=limite,
        offset=offset,
        columns=proyeccion,
    )

    for detalle in detalles:
        detalle_producto = detalle.get("detalles_producto")
        if isinstance(detalle_producto, dict):
            detalle["producto"] = detalle_producto.get("productos")

    return detalles


async def actualizarDetalleVenta(datos: Union[Detalle_venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['producto', 'venta'])

    if id is None:
        return await insert('detalle_venta', payload)
    return await update('detalle_venta', id, payload, key='id')
