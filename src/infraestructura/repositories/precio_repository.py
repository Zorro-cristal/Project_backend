from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerPrecio(filtros=None, limite=100, offset=0, columnas="*"):
    columnas_consulta = columnas
    if columnas_consulta == "*":
        columnas_consulta = "*, detalles_precio(*)"

    if filtros and "detalles_precio.id_detalleproductofk" in filtros:
        columnas_consulta = columnas_consulta.replace(
            "detalles_precio(",
            "detalles_precio!inner(",
            1,
        )

    return await get(
        'precios',
        filters=filtros,
        limit=limite,
        offset=offset,
        columns=columnas_consulta,
    )


async def crearPrecio(datos: dict) -> dict:
    payload = prepararPayloadDb(datos)

    # Asegurar NOT NULL en BD
    if payload.get('valido_desde') is None:
        raise ValueError('valido_desde es obligatorio (NOT NULL en precios)')

    # Normalizar las fechas para almacenarlas como texto ISO en SQLite/libSQL.
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
        'id_preciofk': precio_id,
        'id_detalleproductofk': detalle_cod
    }
    return await insert('detalles_precio', payload)