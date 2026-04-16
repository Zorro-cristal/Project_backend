from src.shell.adaptadores.database.generic_crud import get, insert, update

async def obtenerPrecio(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('precios', filtros, limite, offset)

async def actualizarPrecio(datos, id= 0):
    if id is None:
        return await insert('precio', datos)
    return await update('precio', id, datos)