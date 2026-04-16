from typing import Optional
from pydantic import BaseModel

class CategoriaRequest(BaseModel):
    nombre: str
    estado: int= 1
    descripcion: Optional[str]= None
    
    class Config:
        validate_by_name = True
    
class CategoriaUpdateRequest(BaseModel):
    nombre: Optional[str]= None
    estado: Optional[int]= None
    descripcion: Optional[str]= None
    
    class Config:
        validate_by_name = True