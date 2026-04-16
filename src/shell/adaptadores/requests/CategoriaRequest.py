from typing import Optional
from pydantic import BaseModel

class CategoriaRequest(BaseModel):
    nombre: str
    estado: int= 1
    descripcion: Optional[str]= None
    
    class Config:
        allow_population_by_field_name = True
    
class CategoriaUpdateRequest(BaseModel):
    nombre: Optional[str]= None
    estado: Optional[int]= None
    descripcion: Optional[str]= None
    
    class Config:
        allow_population_by_field_name = True