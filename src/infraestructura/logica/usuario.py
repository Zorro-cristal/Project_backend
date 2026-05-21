from src.infraestructura.database.usuario import obtenerUsuarios, actualizarUsuario
from src.infraestructura.entidad.usuario import Usuario


def build_usuario_entity(payload: dict) -> Usuario:
    valid_fields = {key: value for key, value in payload.items() if key in Usuario.__annotations__}
    return Usuario(**valid_fields)


async def obtener_usuarios(filtros: dict = None, columnas: str = '*'):
    return await obtenerUsuarios(filtros, 100, 0)


async def crear_usuario(payload: dict):
    usuario = build_usuario_entity(payload)
    return await actualizarUsuario(usuario)


async def actualizar_usuario(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarUsuario(payload, id)
