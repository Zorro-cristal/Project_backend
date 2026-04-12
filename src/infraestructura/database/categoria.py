from src.shell.adaptadores.database.generic_crud import get

async def obtenerCategoria(filtros, limite, offset):
    return await get('categorias', filtros, limite, offset)

async def actualizarCategoria(datos, id= 0):
    if (id == 0) {
        return insert('categoria', datos)
    } else {
        return update('categoria', id, datos)
    }