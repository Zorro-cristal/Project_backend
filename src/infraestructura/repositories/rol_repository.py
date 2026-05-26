from typing import Optional, Union

from src.infraestructura.models.rol import Rol
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerRol(filtros: Optional[dict] = None, limite: int = 100, offset: int = 0, columnas: str = "*"):
    return await get('roles', filtros, limite, offset, columns=columnas)

async def actualizarRol(datos: Union[Rol, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if id is None:
        return await insert('roles', payload)
    return await update('roles', id, payload)
