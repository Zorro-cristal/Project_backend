from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.infraestructura.models.usuario import Usuario
from src.shell.flujo.usuario.procesarLogin import procesarLogin
from src.shell.flujo.usuario.gestion import (
    actualizar_usuario_por_id,
    crear_o_actualizar_usuario,
)
from src.infraestructura.services.usuario_service import obtener_usuarios
from src.shell.adapters.requests.usuario_request import (
    UsuarioRequest,
    UsuarioUpdateRequest,
)

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


@router.put("/{id}", summary="Actualizar usuario", description="Actualiza un usuario existente por su ID.")
async def actualizarUsuarioApi(id: int, requestBody: UsuarioUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_usuario_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar usuario parcialmente", description="Actualiza parcialmente un usuario existente por su ID.")
async def patchUsuarioApi(id: int, requestBody: UsuarioUpdateRequest):
    return await actualizarUsuarioApi(id, requestBody)


@router.post("/", summary="Crear usuario", description="Crea un nuevo usuario.")
async def agregarUsuarioApi(requestBody: UsuarioRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_usuario(payload)
    return {"message": result}


@router.get("/", summary="Obtener usuarios", description="Obtiene una lista de usuarios con filtros opcionales.")
async def obtenerUsuariosApi(
    id: Optional[str] = None,
    alias: Optional[str] = None,
    estado: Optional[int] = None,
    id_personaFK: Optional[int] = None,
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if alias is not None:
        filtros["alias"] = alias
    if estado is not None:
        filtros["estado"] = estado
    if id_personaFK is not None:
        filtros["id_personaFK"] = id_personaFK

    result = await obtener_usuarios(filtros)
    return {"message": result}
