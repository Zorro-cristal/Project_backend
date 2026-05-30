from src.infraestructura.models.stock import Stock
from src.infraestructura.repositories.stock_repository import (actualizarStock,
                                                               obtenerStock)
from src.infraestructura.services.detalles_producto_service import \
    obtener_detalles_productos
from src.infraestructura.services.local_service import obtener_locales


def build_stock_entity(payload: dict) -> Stock:
    valid_fields = {key: value for key, value in payload.items() if key in Stock.__annotations__}
    return Stock(**valid_fields)


async def attach_related_data(stocks: list[dict]) -> list[dict]:
    local_ids = {stock.get('id_localfk') for stock in stocks if stock.get('id_localfk')}
    detalle_ids = {stock.get('id_detalleProductofk') for stock in stocks if stock.get('id_detalleProductofk')}

    if local_ids:
        filtros_local = {'id': list(local_ids)}
        locales = await obtener_locales(filtros_local)
        local_map = {local['id']: local for local in (locales or [])}
    else:
        local_map = {}

    if detalle_ids:
        filtros_detalle = {'cod_barra': list(detalle_ids)}
        detalles = await obtener_detalles_productos(filtros_detalle)
        detalle_map = {detalle.get('cod_barra') or detalle.get('id'): detalle for detalle in (detalles or [])}
    else:
        detalle_map = {}

    for stock in stocks:
        local_id = stock.get('id_localfk')
        stock['local'] = local_map.get(local_id)
        detalle_id = stock.get('id_detalleProductofk')
        stock['detalles_producto'] = detalle_map.get(detalle_id)
    return stocks


async def obtener_stocks(filtros: dict = None, columnas: str = '*'):
    stocks = await obtenerStock(filtros=filtros, columnas=columnas)
    if not stocks:
        return stocks
    return await attach_related_data(stocks)


async def crear_stock(payload: dict):
    stock = build_stock_entity(payload)
    return await actualizarStock(stock)


async def actualizar_stock(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarStock(payload, id)
