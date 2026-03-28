from src.shell.adaptadores.database.generic_crud import get

async def obtenerUsuarios(filtros, limite, offset):
    return await get('usuarios', filtros, limite, offset)