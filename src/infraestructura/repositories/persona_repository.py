from typing import Optional, Union

from ..models.persona import Persona
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerPersona(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('personas', filtros, limite, offset)

async def actualizarPersona(datos: Union[Persona, dict], cedula: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if cedula is None:
        return await insert('personas', payload)
    return await update('personas', cedula, payload, key='cedula')
