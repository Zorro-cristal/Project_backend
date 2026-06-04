from typing import Optional

from src.shell.utils import attach_related, validar_fk_existente

from ..models.reserva import Reserva
from ..repositories.reserva_repository import actualizarReserva, obtenerReserva
from .cliente_service import obtener_clientes


def build_reserva_entity(payload: dict) -> Reserva:
    valid_fields = {key: value for key, value in payload.items() if key in Reserva.__annotations__}
    return Reserva(**valid_fields)


async def obtener_reservas(filtros: Optional[dict] = None, columnas: str = '*'):
    reservas = await obtenerReserva(filtros=filtros, columnas=columnas)
    if not reservas:
        return reservas

    # Adjunta cliente (1:1 por FK)
    return await attach_related(
        reservas,
        'id_clientefk',
        obtener_clientes,
        'id',
        'id',
        'cliente',
    )


async def crear_reserva(payload: dict):
    await validar_fk_existente(
        payload.get('id_clientefk'),
        obtener_clientes,
        'id',
        f"Cliente con ID {payload.get('id_clientefk')} no existe",
    )
    reserva = build_reserva_entity(payload)
    return await actualizarReserva(reserva)


async def actualizar_reserva(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    await validar_fk_existente(
        payload.get('id_clientefk'),
        obtener_clientes,
        'id',
        f"Cliente con ID {payload.get('id_clientefk')} no existe",
    )

    return await actualizarReserva(payload, id)

