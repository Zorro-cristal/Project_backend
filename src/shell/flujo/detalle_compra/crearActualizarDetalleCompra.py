from src.infraestructura.services.detalle_compra_service import crear_detalle_compra, actualizar_detalle_compra
from src.infraestructura.services.producto_service import crear_producto


async def crear_o_actualizar_detalle_compra(payload: dict):
    producto_payload = payload.pop('producto', None)
    if producto_payload is not None:
        producto = await crear_producto(producto_payload)
        payload['id_productofk'] = producto.get('id') if isinstance(producto, dict) else getattr(producto, 'id', None)

    return await crear_detalle_compra(payload)


async def actualizar_detalle_compra_por_id(id_detalle: int, payload: dict):
    producto_payload = payload.pop('producto', None)
    if producto_payload is not None:
        producto = await crear_producto(producto_payload)
        payload['id_productofk'] = producto.get('id') if isinstance(producto, dict) else getattr(producto, 'id', None)

    return await actualizar_detalle_compra(id_detalle, payload)
