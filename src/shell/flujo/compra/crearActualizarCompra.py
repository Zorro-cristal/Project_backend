from src.infraestructura.services.compra_service import crear_compra, actualizar_compra
from src.infraestructura.services.cliente_service import crear_cliente
from src.infraestructura.services.local_service import crear_local
from src.infraestructura.services.proveedor_service import crear_proveedor
from src.shell.flujo.detalle_compra.crearActualizarDetalleCompra import crear_o_actualizar_detalle_compra


async def crear_o_actualizar_compra(payload: dict):
    cliente_payload = payload.pop('cliente', None)
    if cliente_payload is not None:
        cliente = await crear_cliente(cliente_payload)
        payload['id_clientefk'] = cliente.get('id') if isinstance(cliente, dict) else getattr(cliente, 'id', None)

    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_local(local_payload)
        payload['id_localfk'] = local.get('id') if isinstance(local, dict) else getattr(local, 'id', None)

    proveedor_payload = payload.pop('proveedor', None)
    if proveedor_payload is not None:
        proveedor = await crear_proveedor(proveedor_payload)
        payload['id_proveedorfk'] = proveedor.get('id') if isinstance(proveedor, dict) else getattr(proveedor, 'id', None)

    detalles = payload.pop('detalles', None)
    compra = await crear_compra(payload)

    if detalles and compra:
        compra_id = compra.get('id') if isinstance(compra, dict) else getattr(compra, 'id', None)
        for detalle_payload in detalles:
            detalle_payload['id_comprafk'] = compra_id
            await crear_o_actualizar_detalle_compra(detalle_payload)

    return compra


async def actualizar_compra_por_id(id_compra: int, payload: dict):
    cliente_payload = payload.pop('cliente', None)
    if cliente_payload is not None:
        cliente = await crear_cliente(cliente_payload)
        payload['id_clientefk'] = cliente.get('id') if isinstance(cliente, dict) else getattr(cliente, 'id', None)

    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_local(local_payload)
        payload['id_localfk'] = local.get('id') if isinstance(local, dict) else getattr(local, 'id', None)

    proveedor_payload = payload.pop('proveedor', None)
    if proveedor_payload is not None:
        proveedor = await crear_proveedor(proveedor_payload)
        payload['id_proveedorfk'] = proveedor.get('id') if isinstance(proveedor, dict) else getattr(proveedor, 'id', None)

    detalles = payload.pop('detalles', None)
    compra = await actualizar_compra(id_compra, payload)

    if detalles and compra:
        for detalle_payload in detalles:
            detalle_payload['id_comprafk'] = id_compra
            await crear_o_actualizar_detalle_compra(detalle_payload)

    return compra
