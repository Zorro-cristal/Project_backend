from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerUsuarios(filtros, limite, offset, columnas= '*'):
    return await get('usuarios', filtros, limite, offset, columns= columnas + ", personas(nombres, apellidos, telefono)")

async def actualizarUsuario(datos, id= 0):
    payload = prepararPayloadDb(datos, exclude_fields=['persona','rol'])
    if id == 0:
        return await insert('usuarios', payload)
    return await update('usuarios', id, payload)