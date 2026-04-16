from typing import Optional
from pydantic import BaseModel, Field

class MarcaRequest(BaseModel):
    nombre: str
    estado: int = 1
    
    class Config:
        validate_by_name = True


class MarcaUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[int] = None

    class Config:
        validate_by_name = True