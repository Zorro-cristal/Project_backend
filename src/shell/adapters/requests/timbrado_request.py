from typing import Optional

from pydantic import BaseModel, Field


class TimbradoBase(BaseModel):
    nro_timbrado: str = Field(..., max_length=15)
    fin_vigencia: str
    nro_inicio: int
    nro_fin: int
    estado: int = 1


class TimbradoUpdate(BaseModel):
    nro_timbrado: Optional[str] = Field(None, max_length=15)
    fin_vigencia: Optional[str] = None
    nro_inicio: Optional[int] = None
    nro_fin: Optional[int] = None
    estado: Optional[int] = None


class EmitirCodNumRequest(BaseModel):
    id_local: int
    id_vendedor: int
