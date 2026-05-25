from typing import Optional, Union

from src.infraestructura.entidad.persona import Persona
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerPersona(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('Persona', filtros, limite, offset)

async def actualizarPersona(datos: Union[Persona, dict], cedula: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if cedula is None:
        return await insert('Persona', payload)
    return await update('Persona', cedula, payload, key='cedula')
