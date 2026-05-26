from typing import Optional, Union

from src.infraestructura.models.permiso import Permiso
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerPermiso(filtros: Optional[dict] = None, limite: int = 100, offset: int = 0, columnas: str = "*"):
    return await get('permisos', filtros, limite, offset, columns=columnas)


async def actualizarPermiso(datos: Union[Permiso, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if id is None:
        return await insert('permisos', payload)
    return await update('permisos', id, payload)
