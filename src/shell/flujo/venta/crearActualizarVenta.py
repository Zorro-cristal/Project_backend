from src.infraestructura.services.venta_service import crear_venta, actualizar_venta
from src.infraestructura.services.venta_service import crear_venta, actualizar_venta
from src.infraestructura.services.usuario_service import crear_usuario
from src.infraestructura.services.cliente_service import crear_cliente
from src.infraestructura.services.local_service import crear_local
from src.shell.flujo.detalle_venta.crearActualizarDetalleVenta import crear_o_actualizar_detalle_venta


async def crear_o_actualizar_venta(payload: dict):
    usuario_payload = payload.pop('usuario', None)
    if usuario_payload is not None:
        usuario = await crear_usuario(usuario_payload)
        payload['id_usuarioFK'] = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)

    cliente_payload = payload.pop('cliente', None)
    if cliente_payload is not None:
        cliente = await crear_cliente(cliente_payload)
        payload['id_clienteFK'] = cliente.get('id') if isinstance(cliente, dict) else getattr(cliente, 'id', None)

    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_local(local_payload)
        payload['id_localFK'] = local.get('id') if isinstance(local, dict) else getattr(local, 'id', None)

    detalles = payload.pop('detalles', None)
    venta = await crear_venta(payload)

    if detalles and venta:
        venta_id = venta.get('id') if isinstance(venta, dict) else getattr(venta, 'id', None)
        for detalle_payload in detalles:
            detalle_payload['id_ventaFK'] = venta_id
            await crear_o_actualizar_detalle_venta(detalle_payload)

    return venta


async def actualizar_venta_por_id(id_venta: int, payload: dict):
    usuario_payload = payload.pop('usuario', None)
    if usuario_payload is not None:
        usuario = await crear_usuario(usuario_payload)
        payload['id_usuarioFK'] = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)

    cliente_payload = payload.pop('cliente', None)
    if cliente_payload is not None:
        cliente = await crear_cliente(cliente_payload)
        payload['id_clienteFK'] = cliente.get('id') if isinstance(cliente, dict) else getattr(cliente, 'id', None)

    local_payload = payload.pop('local', None)
    if local_payload is not None:
        local = await crear_local(local_payload)
        payload['id_localFK'] = local.get('id') if isinstance(local, dict) else getattr(local, 'id', None)

    detalles = payload.pop('detalles', None)
    venta = await actualizar_venta(id_venta, payload)

    if detalles and venta:
        venta_id = id_venta
        for detalle_payload in detalles:
            detalle_payload['id_ventaFK'] = venta_id
            await crear_o_actualizar_detalle_venta(detalle_payload)

    return venta
