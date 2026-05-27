from src.infraestructura.services.caja_service import crear_caja, actualizar_caja
from src.infraestructura.services.usuario_service import crear_usuario, actualizar_usuario


async def crear_o_actualizar_caja(payload: dict):
    usuario_payload = payload.pop('usuario', None)
    if usuario_payload is not None:
        usuario_id = payload.get('id_usuarioFK')
        if usuario_id is not None:
            usuario = await actualizar_usuario(usuario_id, usuario_payload)
        else:
            usuario = await crear_usuario(usuario_payload)
            payload['id_usuarioFK'] = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)

    return await crear_caja(payload)


async def actualizar_caja_por_id(id_caja: int, payload: dict):
    usuario_payload = payload.pop('usuario', None)
    if usuario_payload is not None:
        usuario_id = payload.get('id_usuarioFK')
        if usuario_id is not None:
            usuario = await actualizar_usuario(usuario_id, usuario_payload)
        else:
            usuario = await crear_usuario(usuario_payload)
            payload['id_usuarioFK'] = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)

    return await actualizar_caja(id_caja, payload)
