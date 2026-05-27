from src.infraestructura.services.stock_service import crear_stock, actualizar_stock
from src.shell.flujo.local.crearActualizarLocal import crear_o_actualizar_local


async def crear_o_actualizar_stock(payload: dict):
    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_o_actualizar_local(local_payload)
        payload['id_localFK'] = local.get('id')

    detalle_payload = payload.pop('detalle_producto', None)
    if detalle_payload is not None:
        detalle = await crear_o_actualizar_detalle_producto(detalle_payload)
        # detalle_producto uses cod_barra as key in that module; try to get id or cod
        payload['id_detalleProductoFK'] = detalle.get('cod_barra') or detalle.get('id')

    return await crear_stock(payload)


async def actualizar_stock_por_id(id_stock: int, payload: dict):
    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_o_actualizar_local(local_payload)
        payload['id_localFK'] = local.get('id')

    detalle_payload = payload.pop('detalle_producto', None)
    if detalle_payload is not None:
        detalle = await crear_o_actualizar_detalle_producto(detalle_payload)
        payload['id_detalleProductoFK'] = detalle.get('cod_barra') or detalle.get('id')

    return await actualizar_stock(id_stock, payload)
