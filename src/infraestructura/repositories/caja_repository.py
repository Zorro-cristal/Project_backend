from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.caja import Caja


async def obtenerCaja(filtros=None, limite=100, offset=0, columnas="*"):
    joins = [{
        "table": "usuarios",
        "foreign_key": "id_usuariofk",
        "primary_key": "id",
        "type": "LEFT",
    }, {
        "table": "personas",
        "foreign_key": "id_personafk",
        "source_table": "usuarios",
        "primary_key": "cedula",
        "type": "LEFT",
    }]

    return await get(
        'cajas',
        filtros,
        limite,
        offset,
        order_by='fecha_cierre',
        columns=columnas,
        joins=joins,
    )


async def actualizarCaja(datos: Union[Caja, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario'])

    if id is None:
        return await insert('cajas', payload)
    return await update('cajas', id, payload)
