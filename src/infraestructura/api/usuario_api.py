from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.infraestructura.api.dependencies import permiso_requerido
from src.shared.security.auth_handler import crear_token_acceso
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
    user_for_processing = Usuario(alias=request_body.alias, contra=request_body.contra)
    result = await procesarLogin(user_for_processing)
    
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user_data = result[0]
    # Generar token con el ID y alias
    token = crear_token_acceso(data={"sub": str(user_data['id']), "alias": user_data['alias']})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }


@router.put("/{id}", dependencies=[Depends(permiso_requerido('Usuarios', 'editar'))], summary="Actualizar usuario", description="Actualiza un usuario existente por su ID.")
async def actualizarUsuarioApi(id: int, requestBody: UsuarioUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_usuario(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('Usuarios', 'editar'))], summary="Actualizar usuario parcialmente", description="Actualiza parcialmente un usuario existente por su ID.")
async def patchUsuarioApi(id: int, requestBody: UsuarioUpdateRequest):
    return await actualizarUsuarioApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('Usuarios', 'crear'))], summary="Crear usuario", description="Crea un nuevo usuario.")
async def agregarUsuarioApi(requestBody: UsuarioRequest):
    payload = requestBody.model_dump()
    result = await crear_usuario(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('Usuarios', 'leer'))], summary="Obtener usuarios", description="Obtiene una lista de usuarios con filtros opcionales.")
async def obtenerUsuariosApi(
    id: Optional[str] = None,
    alias: Optional[str] = None,
    estado: Optional[int] = None,
    id_personafk: Optional[int] = None,
mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
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
    # Por defecto ocultar inactivos (estado=0), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = 1

    result = await obtener_usuarios(filtros)
    return {"message": result}
