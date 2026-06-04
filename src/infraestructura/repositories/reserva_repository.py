from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.reserva import Reserva


async def obtenerReserva(filtros=None, limite=100, offset=0, columnas="*"):
    return await get('reservas', filtros, limite, offset, columns=columnas)


async def actualizarReserva(datos: Union[Reserva, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['cliente'])

    if id is None:
        return await insert('reservas', payload)

    return await update('reservas', id, payload)

