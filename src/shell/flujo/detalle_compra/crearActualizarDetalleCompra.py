import logging

from src.infraestructura.services.detalle_compra_service import (
    actualizar_detalle_compra, crear_detalle_compra)
from src.infraestructura.services.stock_service import crear_stock

logger = logging.getLogger(__name__)


def map_detalle_to_stock(detalle_payload: dict) -> dict:
    """Convierte datos del detalle de compra a formato stock"""
    cantidad = detalle_payload.get('cantidad', 0)
    precio = detalle_payload.get('precio', 0)
    # El frontend envía cod_barra que es la llave primaria de detalles_producto
    id_detalleproductofk = detalle_payload.get('cod_barra')
    id_localfk = detalle_payload.get('id_localfk')
    fecha_vencimiento = detalle_payload.get('fecha_vencimiento')
    lote = detalle_payload.get('lote', '')
    
    if not id_detalleproductofk or not id_localfk:
        logger.warning(f"Faltan campos requeridos para stock: cod_barra={id_detalleproductofk}, id_localfk={id_localfk}")
        return None
    
    # Crear el stock con la cantidad comprada como cant_deposito
    return {
        'cant_deposito': cantidad,
        'cant_mostrador': 0,
        'cant_reservado': 0,
        'precio': precio,
        'lote': lote,
        'id_detalleproductofk': id_detalleproductofk,
        'id_localfk': id_localfk,
        'fecha_vencimiento': fecha_vencimiento
    }


async def crear_o_actualizar_detalle_compra(payload: dict):
    # Extraer datos del stock del payload
    stock_payload = payload.pop('stock', None)
    id_stockfk = payload.get('id_stockfk')
    
    logger.info(f"Payload recibido para detalle_compra: {payload}")
    logger.info(f"Stock payload inicial: {stock_payload}, id_stockfk: {id_stockfk}")
    
    # Si no hay stock object ni id_stockfk válido, construir desde campos sueltos del frontend
    if stock_payload is None and (id_stockfk is None or id_stockfk == 0):
        stock_payload = map_detalle_to_stock(payload)
        logger.info(f"Stock payload construido desde detalle: {stock_payload}")
    
    # Siempre crear stock si no tenemos id_stockfk válido
    if stock_payload is not None:
        try:
            logger.info(f"Creando stock con payload: {stock_payload}")
            stock = await crear_stock(stock_payload)
            logger.info(f"Stock creado exitosamente: {stock}")
            
            nuevo_stock_id = stock.get('id') if isinstance(stock, dict) else getattr(stock, 'id', None)
            logger.info(f"Nuevo stock ID obtenido: {nuevo_stock_id}")
            
            if not nuevo_stock_id:
                raise ValueError(f"No se pudo obtener el ID del stock creado. Stock response: {stock}")
            
            payload['id_stockfk'] = nuevo_stock_id
            logger.info(f"ID stock asignado al payload: {nuevo_stock_id}")
        except Exception as e:
            logger.error(f"Error al crear stock: {str(e)}")
            raise
    elif id_stockfk is None or id_stockfk == 0:
        raise ValueError('Se requiere datos del stock para crear un nuevo registro')

    logger.info(f"Payload final antes de crear detalle_compra: {payload}")
    return await crear_detalle_compra(payload)


async def actualizar_detalle_compra_por_id(id_detalle: int, payload: dict):
    # Extraer datos del stock del payload
    stock_payload = payload.pop('stock', None)
    id_stockfk = payload.get('id_stockfk')
    
    logger.info(f"Actualizando detalle_compra {id_detalle}: stock_payload={stock_payload}, id_stockfk={id_stockfk}")
    
    # Si no hay stock object ni id_stockfk válido, construir desde campos sueltos del frontend
    if stock_payload is None and (id_stockfk is None or id_stockfk == 0):
        stock_payload = map_detalle_to_stock(payload)
        logger.info(f"Stock payload construido para actualización: {stock_payload}")
    
    # Siempre crear stock si no tenemos id_stockfk válido
    if stock_payload is not None:
        try:
            logger.info(f"Creando stock para actualización con payload: {stock_payload}")
            stock = await crear_stock(stock_payload)
            logger.info(f"Stock creado exitosamente: {stock}")
            
            nuevo_stock_id = stock.get('id') if isinstance(stock, dict) else getattr(stock, 'id', None)
            logger.info(f"Nuevo stock ID para actualización: {nuevo_stock_id}")
            
            if not nuevo_stock_id:
                raise ValueError(f"No se pudo obtener el ID del stock creado. Stock response: {stock}")
            
            payload['id_stockfk'] = nuevo_stock_id
            logger.info(f"ID stock asignado para actualización: {nuevo_stock_id}")
        except Exception as e:
            logger.error(f"Error al crear stock para actualización: {str(e)}")
            raise
    elif id_stockfk is None or id_stockfk == 0:
        raise ValueError('Se requiere datos del stock para crear un nuevo registro')

    logger.info(f"Payload final para actualizar detalle_compra: {payload}")
    return await actualizar_detalle_compra(id_detalle, payload)
