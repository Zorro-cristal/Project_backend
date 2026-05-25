from src.infraestructura.database.usuario import obtenerUsuarios, actualizarUsuario
from src.infraestructura.entidad.usuario import Usuario
from src.infraestructura.logica.persona import (
    actualizar_persona,
    crear_persona,
    obtener_personas,
)


def build_usuario_entity(payload: dict) -> Usuario:
    valid_fields = {key: value for key, value in payload.items() if key in Usuario.__annotations__}
    return Usuario(**valid_fields)


async def attach_persona_data(usuarios: list[dict]) -> list[dict]:
    persona_ids = {usuario.get('id_personaFK') for usuario in usuarios if usuario.get('id_personaFK')}
    if not persona_ids:
        return usuarios

    filtros = {'cedula': list(persona_ids)}
    personas = await obtener_personas(filtros)

    persona_map = {persona['cedula']: persona for persona in (personas or [])}
    for usuario in usuarios:
        persona_id = usuario.get('id_personaFK')
        usuario['persona'] = persona_map.get(persona_id)
    return usuarios


async def obtener_usuarios(filtros: dict = None, columnas: str = '*'):
    usuarios = await obtenerUsuarios(filtros, 100, 0)
    if not usuarios:
        return usuarios
    return await attach_persona_data(usuarios)


async def crear_usuario(payload: dict):
    usuario = build_usuario_entity(payload)
    return await actualizarUsuario(usuario)


async def actualizar_usuario(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarUsuario(payload, id)
