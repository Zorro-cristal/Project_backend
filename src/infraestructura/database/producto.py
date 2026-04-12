from src.shell.adaptadores.database.generic_crud import get

async def obtenerProducto(filtros, limite, offset):
    return await get('producto', filtros, limite, offset)