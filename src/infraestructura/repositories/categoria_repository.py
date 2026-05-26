from typing import Optional, Union

from src.infraestructura.models.categoria import Categoria
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

async def obtenerCategoria(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('categorias', filtros, limite, offset, columns= columnas)

async def actualizarCategoria(datos: Union[Categoria, dict], id: Optional[int]= None):
    payload = prepararPayloadDb(datos)

    if id is None:
        return await insert('categorias', payload)
    return await update('categorias', id, payload)