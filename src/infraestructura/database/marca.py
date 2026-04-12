from src.shell.adaptadores.database.generic_crud import get

async def obtenerMarca(filtros, limite, offset):
    return await get('marcas', filtros, limite, offset)

async def actualizarMarca(datos, id= 0):
    if (id == 0) {
        return insert('marca', datos)
    } else {
        return update('marca', id, datos)
    }