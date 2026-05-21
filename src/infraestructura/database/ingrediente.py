from typing import Optional, Union

from src.infraestructura.entidad.ingrediente import Ingrediente
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerIngrediente(filtros: Optional[dict] = None, limite: int = 100, offset: int = 0, columnas: str = "*"):
    return await get('ingredientes', filtros, limite, offset, columns=columnas)

async def actualizarIngrediente(datos: Union[Ingrediente, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    if id is None:
        return await insert('ingredientes', payload)
    return await update('ingredientes', id, payload)
