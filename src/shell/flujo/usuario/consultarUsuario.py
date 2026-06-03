from src.infraestructura.services.usuario_service import (
    obtener_usuarios as obtener_usuarios_service,
)


async def obtener_usuarios(filtros: dict = None):
    return await obtener_usuarios_service(filtros)
