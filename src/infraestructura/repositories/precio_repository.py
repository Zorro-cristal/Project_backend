from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerPrecio(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('precios', filters=filtros, limit=limite, offset=offset, columns=columnas)


async def crearPrecio(datos: dict) -> dict:
    payload = prepararPayloadDb(datos)

    # Asegurar NOT NULL en BD
    if payload.get('valido_desde') is None:
        raise ValueError('valido_desde es obligatorio (NOT NULL en precios)')

    # Convertir a formato compatible con Supabase/Postgres
    # (si llega como datetime, pasarlo a isoformat; si llega como string, dejarlo)
    if hasattr(payload['valido_desde'], 'isoformat'):
        payload['valido_desde'] = payload['valido_desde'].isoformat()

    if 'valido_hasta' in payload and payload['valido_hasta'] is not None:
        if hasattr(payload['valido_hasta'], 'isoformat'):
            payload['valido_hasta'] = payload['valido_hasta'].isoformat()

    return await insert('precios', payload)

async def crearDetallePrecio(datos: dict) -> dict:
    payload = prepararPayloadDb(datos)
    return await insert('detalles_precio', payload)

async def actualizarPrecio(datos: dict, id: int | None = None) -> dict:
    payload = prepararPayloadDb(datos)
    if 'valido_hasta' in payload:
        payload['valido_hasta'] = payload.pop('valido_hasta')

    if id is None:
        return await insert('precios', payload)
    return await update('precios', id, payload)


async def vincular_precio_detalle(precio_id: int, detalle_cod: str) -> dict:
    payload = {
        'precio_id': precio_id,
        'detalles_producto_cod': detalle_cod
    }
    return await insert('detalles_precio', payload)