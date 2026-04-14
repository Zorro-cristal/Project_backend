from typing import Optional

from src.shell.adaptadores.database.generic_crud import get, insert, update

async def obtenerProducto(filtros: Optional[dict] = None, limite: Optional[int]= 100, offset: Optional[int]= 0, columnas: str= "*"):
    return await get('productos', filtros, limite, offset, columns=columnas)

async def actualizarProducto(datos, id= 0): # Se corrige el nombre de la función de 'actualizarUsuario' a 'actualizarProducto'
    if (id == 0):
        return insert('productos', datos)
    else:
        return update('productos', id, datos)