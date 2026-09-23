from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.persona import Persona


async def obtenerPersona(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('personas', filtros, limite, offset)

async def actualizarPersona(datos: Union[Persona, dict], cedula: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if cedula is not None:
        existe = await obtenerPersona(filtros={'cedula': cedula})
        if existe and len(existe) > 0:
            return await update('personas', cedula, payload, key='cedula')
    
    return await insert('personas', payload)

