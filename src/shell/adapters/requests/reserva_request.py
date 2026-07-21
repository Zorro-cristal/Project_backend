from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.cliente_request import (ClienteRequest,
                                                         ClienteUpdateRequest)


class ReservaRequest(BaseModel):
    fecha_reserva: str
    cantidad_personas: int
    observacion: Optional[str] = None
    estado: Optional[int] = 1
    tiempo_ocupacion: Optional[str] = None
    id_clientefk: Optional[int] = None
    cliente: Optional[ClienteRequest] = None

    class Config:
        validate_by_name = True


class ReservaUpdateRequest(BaseModel):
    fecha_reserva: Optional[str] = None
    cantidad_personas: Optional[int] = None
    observacion: Optional[str] = None
    estado: Optional[int] = None
    tiempo_ocupacion: Optional[str] = None
    id_clientefk: Optional[int] = None
    cliente: Optional[ClienteUpdateRequest] = None

    class Config:
        validate_by_name = True

