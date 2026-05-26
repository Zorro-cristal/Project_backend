from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerDetallePrecio(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('detalles_precio', filtros, limite, offset, columns=columnas)


async def crear_detalle_precio(datos: dict) -> dict:
    payload = prepararPayloadDb(datos)
    return await insert('detalles_precio', payload)


async def actualizarDetallePrecio(datos: dict, id: int | None = None) -> dict:
    payload = prepararPayloadDb(datos)
    if id is None:
        return await insert('detalles_precio', payload)
    return await update('detalles_precio', id, payload)