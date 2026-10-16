from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.detalle_compra import Detalle_compra


async def obtenerDetalleCompra(filtros=None, limite=100, offset=0, columnas="*"):
    joins = []
    
    # Añadir producto si no está en columnas y se necesita la relación con detalle_compra
    if "producto" not in columnas.lower():
        joins.append({
            "table": "productos",
            "foreign_key": "id_productofk",
            "primary_key": "id",
            "type": "LEFT",
        })

    # Añadir compra si no está en columnas y se necesita la relación con detalle_compra  
    if "compra" not in columnas.lower():
        joins.append({
            "table": "compras",
            "foreign_key": "id_comprafk",
            "primary_key": "id",
            "type": "LEFT",
        })

    return await get(
        'detalle_compra', 
        filters=filtros, 
        limit=limite, 
        offset=offset, 
        columns=columnas,
        joins=joins if len(joins) > 0 else None,
    )


async def actualizarDetalleCompra(datos: Union[Detalle_compra, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['producto', 'compra'])

    if id is None:
        return await insert('detalle_compra', payload)
    return await update('detalle_compra', id, payload, key='id_detalle_compra')
