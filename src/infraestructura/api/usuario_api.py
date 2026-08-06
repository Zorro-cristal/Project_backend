from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.infraestructura.api.dependencies import permiso_requerido
from src.shared.security.auth_handler import crear_token_acceso
from src.shell.adapters.database.generic_crud import count
from src.shell.adapters.requests.usuario_request import (UsuarioRequest,
                                                         UsuarioUpdateRequest)
from src.shell.flujo.usuario.procesarLogin import procesarLogin

from ..models.usuario import Usuario
from ..services.usuario_service import (actualizar_usuario, crear_usuario,
                                        obtener_usuarios)
from .schemas.relational_sanitizers import UsuarioListResponse

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


@router.get(
    "/",
    dependencies=[Depends(permiso_requerido('Usuarios', 'leer'))],
    summary="Obtener usuarios",
    description="Obtiene una lista de usuarios con filtros opcionales.",
    response_model=UsuarioListResponse,
)
async def obtenerUsuariosApi(
    nombre_completo: Optional[str] = Query(None, description="Buscar por nombre completo de la persona asociada (nombre o apellido, contiene)"),
    id: Optional[str] = None,
    alias: Optional[str] = None,
    estado: Optional[int] = None,
    id_personafk: Optional[int] = None,
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
):
    filtros = {}
    if nombre_completo is not None:
        filtros["nombre_completo"] = nombre_completo
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


@router.post("/usuario_test", summary="Crear usuarios de prueba", description="Crea 5 usuarios de prueba (alias y contra iguales, contra hasheada) solo si NO existe ningún usuario en la base de datos.")
async def usuarioTest():
    # Si existe al menos un usuario en la BD, no creamos nada
    total_usuarios = await count("usuarios")
    if total_usuarios and total_usuarios > 0:
        return {
            "message": "No se crearon usuarios: ya existen usuarios en la base de datos",
            "total_usuarios_existentes": total_usuarios,
            "creados": [],
        }

    usuarios_test = [
        {"id": 1, "contra": "admin", "alias": "admin", "estado": 1, "id_rolfk": 1, "id_personafk": 1000001},
        {"id": 2, "contra": "ana_caja", "alias": "ana_caja", "estado": 1, "id_rolfk": 2, "id_personafk": 1000002},
        {"id": 3, "contra": "luis_caja2", "alias": "luis_caja2", "estado": 1, "id_rolfk": 2, "id_personafk": 1000003},
        {"id": 4, "contra": "marta_mozo", "alias": "marta_mozo", "estado": 1, "id_rolfk": 3, "id_personafk": 1000004},
        {"id": 5, "contra": "diego_mozo", "alias": "diego_mozo", "estado": 1, "id_rolfk": 3, "id_personafk": 1000005},
    ]

    creados = []
    for payload in usuarios_test:
        result = await crear_usuario(payload)
        creados.append(result)

    return {
        "message": "Usuarios de prueba creados",
        "creados": creados,
        "total_usuarios_creados": len(creados),
    }
