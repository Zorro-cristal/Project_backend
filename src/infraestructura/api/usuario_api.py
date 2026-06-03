from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.shell.adapters.requests.usuario_request import (UsuarioRequest,
                                                         UsuarioUpdateRequest)
from src.shell.flujo.usuario.procesarLogin import procesarLogin

from ..models.usuario import Usuario
from ..services.usuario_service import (actualizar_usuario, crear_usuario,
                                        obtener_usuarios)

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
    result = await actualizar_usuario(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar usuario parcialmente", description="Actualiza parcialmente un usuario existente por su ID.")
async def patchUsuarioApi(id: int, requestBody: UsuarioUpdateRequest):
    return await actualizarUsuarioApi(id, requestBody)


@router.post("/", summary="Crear usuario", description="Crea un nuevo usuario.")
async def agregarUsuarioApi(requestBody: UsuarioRequest):
    payload = requestBody.model_dump()
    result = await crear_usuario(payload)
    return {"message": result}


@router.get("/", summary="Obtener usuarios", description="Obtiene una lista de usuarios con filtros opcionales.")
async def obtenerUsuariosApi(
    id: Optional[str] = None,
    alias: Optional[str] = None,
    estado: Optional[int] = None,
    id_personafk: Optional[int] = None,
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if alias is not None:
        filtros["alias"] = alias
    if estado is not None:
        filtros["estado"] = estado
    if id_personafk is not None:
        filtros["id_personafk"] = id_personafk

    result = await obtener_usuarios(filtros)
    return {"message": result}
