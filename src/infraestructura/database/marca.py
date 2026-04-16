from typing import Optional, Union

from src.infraestructura.entidad.marca import Marca
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import prepare_payload_for_db

async def obtenerMarca(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('marcas', filtros, limite, offset)

async def actualizarMarca(datos: Union[Marca, dict], id: Optional[int] = None):
    payload = prepare_payload_for_db(datos)

    if id is None:
        return await insert('marcas', payload)
    return await update('marcas', id, payload)