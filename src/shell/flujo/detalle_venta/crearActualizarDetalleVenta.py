from src.infraestructura.services.detalle_venta_service import crear_detalle_venta, actualizar_detalle_venta
from src.infraestructura.services.producto_service import crear_producto


async def crear_o_actualizar_detalle_venta(payload: dict):
    producto_payload = payload.pop('producto', None)
    if producto_payload is not None:
        producto = await crear_producto(producto_payload)
        payload['id_productoFK'] = producto.get('id') if isinstance(producto, dict) else getattr(producto, 'id', None)

    return await crear_detalle_venta(payload)


async def actualizar_detalle_venta_por_id(id_detalle: int, payload: dict):
    producto_payload = payload.pop('producto', None)
    if producto_payload is not None:
        producto = await crear_producto(producto_payload)
        payload['id_productoFK'] = producto.get('id') if isinstance(producto, dict) else getattr(producto, 'id', None)

    return await actualizar_detalle_venta(id_detalle, payload)
