
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Vendedor:
    salario: float
    comision: float
    estado: int = 1
    cod_num: Optional[str] = None
    id_usuariofk: Optional[int] = None
    id: Optional[int] = None
