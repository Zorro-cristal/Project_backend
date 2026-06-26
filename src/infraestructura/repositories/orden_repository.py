from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.orden import Orden


async def obtenerOrdenes(filtros: Optional[dict] = None, limite: int = 100, offset: int = 0, columnas: str = "*"):
    return await get('ordenes', filtros, limite, offset, columns=columnas)


async def actualizarOrden(datos: Union[Orden, dict], id: Optional[int] = None):
    # Nota: la tabla `ordenes` no tiene campos compuestos; si llegan relaciones
    # (ej: mesa, precio) se excluyen para no romper el insert/update.
    payload = prepararPayloadDb(datos, exclude_fields=['mesa', 'precio'])

    if id is not None:
        # En update, no sobrescribir con None
        payload = {k: v for k, v in payload.items() if v is not None}

    if id is None:
        return await insert('ordenes', payload)
    return await update('ordenes', id, payload)

