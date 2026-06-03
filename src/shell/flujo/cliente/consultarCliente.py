from src.infraestructura.services.cliente_service import (
    obtener_clientes as obtener_clientes_service,
)


async def obtener_clientes(filtros: dict = None):
    return await obtener_clientes_service(filtros)
