from src.shell.adaptadores.database.generic_crud import get

async def obtenerUsuarios(filtros, limite, offset):
    return await get('usuarios', filtros, limite, offset)

async def actualizarUsuario(datos, id= 0):
    if (id == 0) {
        return insert('usuario', datos)
    } else {
        return update('usuario', id, datos)
    }