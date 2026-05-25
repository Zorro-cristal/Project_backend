from typing import Optional, Union

from src.infraestructura.entidad.cliente import Cliente
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerCliente(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('clientes', filtros, limite, offset)

async def actualizarCliente(datos: Union[Cliente, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['persona'])

    if id is None:
        return await insert('clientes', payload)
    return await update('clientes', id, payload)
