from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Clima:
    temperatura: float
    sensacion_termica: float
    humedad: float
    velocidad_viento: float
    weather_code: int
    fecha: datetime
    precipitaciones: float
    lluvia: float

@dataclass(frozen=True)
class PronosticoClimatico:
    temperatura_min: float
    temperatura_max: float
    velocidad_viento: float
    lluvia: float
    recipitaciones: float
    probabilidad_precipitaciones: float
    fecha: datetime