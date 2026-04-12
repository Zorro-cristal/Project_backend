from src.shell.adaptadores.database.generic_crud import get

async def obtenerPrecio(filtros, limite, offset):
    return await get('precios', filtros, limite, offset)

async def actualizarPrecio(datos, id= 0):
    if (id == 0) {
        return insert('precio', datos)
    } else {
        return update('precio', id, datos)
    }