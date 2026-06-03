from src.infraestructura.services.stock_service import (
    obtener_stocks as obtener_stocks_service,
)


async def obtener_stocks(filtros: dict = None):
    return await obtener_stocks_service(filtros)
