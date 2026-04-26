from fastapi import APIRouter
from pydantic import BaseModel

from src.infraestructura.entidad.usuario import Usuario
from src.shell.flujo.usuario.procesarLogin import procesarLogin

router = APIRouter()

# Define un modelo Pydantic para el cuerpo de la solicitud de inicio de sesión
class UsuarioLoginRequest(BaseModel):
    alias: str
    contra: str

@router.post("/login", summary="Iniciar sesión", description="Procesa el inicio de sesión de un usuario con alias y contraseña.")
async def login(request_body: UsuarioLoginRequest):
    # Creamos una instancia de Usuario (entidad) para pasar a procesarLogin.
    # Asignamos un ID ficticio (0) ya que el ID real no es parte de la solicitud de login y no se usa en procesarLogin.
    user_for_processing = Usuario(alias=request_body.alias, contra=request_body.contra)
    result = await procesarLogin(user_for_processing)
    return {"message": result} 
