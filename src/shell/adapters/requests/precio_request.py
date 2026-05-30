from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PrecioRequest(BaseModel):
    monto: int
    id_detalleProductofk: int
    valido_desde: datetime
    valido_hasta: Optional[datetime]= None
    
    class Config:
        validate_by_name = True

class PrecioUpdateRequest(BaseModel):
    monto: Optional[int] = None
    valido_desde: Optional[datetime] = None
    valido_hasta: Optional[datetime] = None
    
    class Config:
        validate_by_name = True