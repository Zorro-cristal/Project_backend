from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.detalle_venta import Detalle_venta


async def obtenerDetalleVenta(filtros=None, limite=100, offset=0, columnas="*"):
    joins = []
    
    # Añadir producto si no está en columnas y se necesita la relación con detalle_venta
    if "producto" not in columnas.lower():
        joins.append({
            "table": "productos",
            "foreign_key": "id_productofk",
            "primary_key": "id",
            "type": "LEFT",
        })

    # Añadir venta si no está en columnas y se necesita la relación con detalle_venta  
    if "venta" not in columnas.lower():
        joins.append({
            "table": "ventas",
            "foreign_key": "id_ventafk",
            "primary_key": "id",
            "type": "LEFT",
        })

    return await get(
        'detalle_venta',
        filters=filtros,
        limit=limite,
        offset=offset,
        columns=columnas,
        joins=joins if len(joins) > 0 else None,
    )


async def actualizarDetalleVenta(datos: Union[Detalle_venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['producto', 'venta'])

    if id is None:
        return await insert('detalle_venta', payload)
    return await update('detalle_venta', id, payload, key='id')
