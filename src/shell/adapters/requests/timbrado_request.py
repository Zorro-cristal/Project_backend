from typing import Optional

from pydantic import BaseModel, Field


class TimbradoBase(BaseModel):
    nro_timbrado: int
    fin_vigencia: str
    estado: int = 1


class TimbradoUpdate(BaseModel):
    nro_timbrado: Optional[int] = None
    fin_vigencia: Optional[str] = None
    estado: Optional[int] = None


class EmitirCodNumRequest(BaseModel):
    id_local: int
    id_vendedor: int
