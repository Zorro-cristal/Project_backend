from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.cliente import Cliente


async def obtenerCliente(filtros= None, limite= 100, offset= 0, columnas= "*"):
    joins = [{
        "table": "personas",
        "foreign_key": "id_personafk",
        "primary_key": "cedula",
        "type": "LEFT",
    }]
    return await get(
        'clientes',
        filtros,
        limite,
        offset,
        columns=columnas + ", personas(cedula, nombres, apellidos, telefono, nacionalidad)",
        joins=joins,
    )

async def actualizarCliente(datos: Union[Cliente, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['persona'])

    if id is None:
        return await insert('clientes', payload)
    return await update('clientes', id, payload)
