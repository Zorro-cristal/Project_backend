from src.shell.utils import attach_related

from ..models.stock import Stock
from ..repositories.stock_repository import actualizarStock, obtenerStock
from .detalles_producto_service import obtener_detalles_productos
from .local_service import obtener_locales


def build_stock_entity(payload: dict) -> Stock:
    valid_fields = {key: value for key, value in payload.items() if key in Stock.__annotations__}
    return Stock(**valid_fields)


async def attach_related_data(stocks: list[dict]) -> list[dict]:
    # One-to-one: local
    stocks = await attach_related(stocks, 'id_localfk', obtener_locales, 'id', 'id', 'local')

    # One-to-one/flexible: detalles_producto puede referenciar por 'cod_barra' o por 'id'
    detalle_ids = {stock.get('id_detalleproductofk') for stock in stocks if stock.get('id_detalleproductofk')}
    detalle_map = {}
    if detalle_ids:
        # Primero intentar buscar por cod_barra
        filtros_detalle = {'cod_barra': list(detalle_ids)}
        detalles = await obtener_detalles_productos(filtros_detalle, include_producto=True)
        if not detalles:
            # Fallback a buscar por id
            filtros_detalle = {'id': list(detalle_ids)}
            detalles = await obtener_detalles_productos(filtros_detalle, include_producto=True)

        detalle_map = {detalle.get('cod_barra') or detalle.get('id'): detalle for detalle in (detalles or [])}

    for stock in stocks:
        detalle_id = stock.get('id_detalleproductofk')
        stock['detalles_producto'] = detalle_map.get(detalle_id)

    return stocks


async def obtener_stocks(filtros: dict = None, columnas: str = '*'):
    filtros = filtros or {}

    # Filtro especial: con_stock => (cant_mostrador > 0 OR cant_deposito > 0)
    # Implementación directa en Supabase (generic_crud no soporta OR/gt por nombres de campo arbitrarios)
    if filtros.get("con_stock") == 1:
        from src.infraestructura.config.supabase import get_supabase_client

        base_filtros = {k: v for k, v in filtros.items() if k != "con_stock"}

        client = get_supabase_client()

        # Consulta por cant_mostrador > 0
        q1 = client.table("stocks").select(columnas)
        for field, value in base_filtros.items():
            q1 = q1.eq(field, value)
        q1 = q1.gt("cant_mostrador", 0).order("fecha_vencimiento", desc=False)

        r1 = q1.execute()
        stocks_mostrador = r1.data or []

        # Consulta por cant_deposito > 0
        q2 = client.table("stocks").select(columnas)
        for field, value in base_filtros.items():
            q2 = q2.eq(field, value)
        q2 = q2.gt("cant_deposito", 0).order("fecha_vencimiento", desc=False)

        r2 = q2.execute()
        stocks_deposito = r2.data or []

        # Unir sin duplicados por id
        por_id = {}
        for s in stocks_mostrador + stocks_deposito:
            _id = s.get("id")
            if _id is not None:
                por_id[_id] = s
            else:
                por_id[id(s)] = s

        stocks = list(por_id.values())
    else:
        stocks = await obtenerStock(filtros=filtros, columnas=columnas)

    if not stocks:
        return stocks
    return await attach_related_data(stocks)


async def crear_stock(payload: dict):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Recibido payload para crear stock: {payload}")
    
    try:
        stock = build_stock_entity(payload)
        logger.info(f"Entidad Stock construida: {stock}")
        
        result = await actualizarStock(stock)
        logger.info(f"Resultado de actualizarStock: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error al crear stock: {str(e)}")
        raise


async def actualizar_stock(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarStock(payload, id)
