
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .persona import Persona


@dataclass(frozen=True)
class Vendedor:
    salario: float
    comision: float
    estado: int = 1
    cod_num: Optional[str] = None
    id_personafk: Optional[int]= None
    persona: Optional[Persona]= None
    id: Optional[int] = None
