from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.caja import Caja


async def obtenerCaja(filtros=None, limite=100, offset=0, columnas="*"):
    joins = [{
        "table": "usuarios",
        "foreign_key": "id_usuariofk",
        "primary_key": "cedula",
        "type": "LEFT",
    }]
    
    # Añadir la relación personas a través de usuarios si no está ya en columnas
    if "personas" not in columnas.lower():
        columns = f"{columnas}, usuarios(personas(nombres, apellidos, telefono))"
    else:
        columns = columnas
    
    joins.append({
        "table": "personas",
        "foreign_key": "id_personafk",
        "primary_key": "cedula",
        "type": "LEFT",
    })

    return await get(
        'cajas',
        filtros,
        limite,
        offset,
        order_by='fecha_cierre',
        columns=columns,
        joins=joins,
    )


async def actualizarCaja(datos: Union[Caja, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario'])

    if id is None:
        return await insert('cajas', payload)
    return await update('cajas', id, payload)
