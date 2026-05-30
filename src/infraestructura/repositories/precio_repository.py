from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerPrecio(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('precios', filters=filtros, limit=limite, offset=offset, columns=columnas)


async def crear_precio(datos: dict) -> dict:
    """Inserta un registro en la tabla `precios`.
    Traduce `valido_hasta` -> `fecha_hasta` para la columna de la BD.
    """
    payload = prepararPayloadDb(datos)
    # mapear nombre de campo a la columna de la tabla
    if 'valido_hasta' in payload:
        payload['fecha_hasta'] = payload.pop('valido_hasta')

    return await insert('precios', payload)


async def actualizarPrecio(datos: dict, id: int | None = None) -> dict:
    payload = prepararPayloadDb(datos)
    if 'valido_hasta' in payload:
        payload['fecha_hasta'] = payload.pop('valido_hasta')

    if id is None:
        return await insert('precios', payload)
    return await update('precios', id, payload)


async def vincular_precio_detalle(precio_id: int, detalle_cod: str) -> dict:
    payload = {
        'precio_id': precio_id,
        'detalles_producto_cod': detalle_cod
    }
    return await insert('detalles_precio', payload)