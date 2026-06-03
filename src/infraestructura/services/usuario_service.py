from ..models.usuario import Usuario
from ..repositories.usuario_repository import (
    actualizarUsuario, obtenerUsuarios)
from .persona_service import (actualizar_persona,
                                                          crear_persona,
                                                          obtener_personas)
from .rol_service import obtener_roles
from src.shared.security.password_hasher import hash_password


def build_usuario_entity(payload: dict) -> Usuario:
    valid_fields = {key: value for key, value in payload.items() if key in Usuario.__annotations__}
    return Usuario(**valid_fields)




def _hash_if_needed(payload: dict) -> dict:
    """Hashea la contraseña si viene en el payload.

    - Si 'contra' no está, no toca.
    - Si 'contra' ya parece hash (empieza con $2b/$2a/$2y), no lo rehashea.
      (Esto ayuda en actualizaciones parciales donde el backend reenvía el valor.)
    """
    if not isinstance(payload, dict):
        return payload

    if 'contra' not in payload:
        return payload

    contra = payload.get('contra')
    if contra is None:
        return payload

    if isinstance(contra, str) and (contra.startswith('$2a$') or contra.startswith('$2b$') or contra.startswith('$2y$')):
        return payload

    payload = dict(payload)
    payload['contra'] = hash_password(contra)
    return payload



async def attach_persona_data(usuarios: list[dict]) -> list[dict]:
    persona_ids = {usuario.get('id_personafk') for usuario in usuarios if usuario.get('id_personafk')}
    if not persona_ids:
        return usuarios

    filtros = {'cedula': list(persona_ids)}
    personas = await obtener_personas(filtros)

    persona_map = {persona['cedula']: persona for persona in (personas or [])}
    for usuario in usuarios:
        persona_id = usuario.get('id_personafk')
        usuario['persona'] = persona_map.get(persona_id)
    return usuarios


async def attach_rol_data(usuarios: list[dict]) -> list[dict]:
    rol_ids = {usuario.get('id_rolfk') for usuario in usuarios if usuario.get('id_rolfk')}
    if not rol_ids:
        return usuarios

    filtros = {'id': list(rol_ids)}
    roles = await obtener_roles(filtros=filtros)

    rol_map = {rol['id']: rol for rol in (roles or []) if rol.get('id') is not None}
    for usuario in usuarios:
        rol_id = usuario.get('id_rolfk')
        usuario['rol'] = rol_map.get(rol_id)
    return usuarios


async def obtener_usuarios(filtros: dict = None, columnas: str = '*'):
    usuarios = await obtenerUsuarios(filtros, 100, 0)
    if not usuarios:
        return usuarios

    usuarios = await attach_persona_data(usuarios)
    return await attach_rol_data(usuarios)



async def crear_usuario(payload: dict):
    payload = _hash_if_needed(payload)
    usuario = build_usuario_entity(payload)
    return await actualizarUsuario(usuario)


async def actualizar_usuario(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    payload = _hash_if_needed(payload)
    return await actualizarUsuario(payload, id)
