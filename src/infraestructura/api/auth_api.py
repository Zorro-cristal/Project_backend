"""API de autenticación y ejemplos de rutas protegidas por scopes.

Contiene:
1. ``POST /login``: autentica un usuario y emite un token JWT con scopes.
2. Ejemplos de rutas protegidas con ``checkScope``:
   - ``GET /ventas`` → requiere ``ventas:leer``.
   - ``POST /ventas/{id}/anular`` → requiere ``ventas_anular:eliminar``.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.infraestructura.services.auth_service import autenticar_usuario
from src.shared.security.auth_handler import crear_token_acceso
from src.shared.security.scopes import checkScope

router = APIRouter()


# ---------------------------------------------------------------------------
# Modelos de entrada/salida
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Cuerpo de la solicitud de inicio de sesión."""

    alias: str
    contra: str


# ---------------------------------------------------------------------------
# Endpoint de autenticación (/login)
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    summary="Iniciar sesión",
    description=(
        "Autentica un usuario por alias y contraseña. Realiza el JOIN entre "
        "Usuario, Rol, Permiso_rol y Permiso, filtra permisos activos "
        "(estado=1), construye los scopes planos 'recurso:accion' y devuelve "
        "un token JWT con id_usuario, alias, rol y scopes."
    ),
)
async def login(request_body: LoginRequest):
    """Procesa el inicio de sesión y emite el token JWT con scopes.

    Args:
        request_body: Alias y contraseña del usuario.

    Returns:
        Dict con el ``access_token``, el ``token_type`` y la información
        básica del usuario junto con su lista plana de ``scopes``.

    Raises:
        HTTPException(401): Si las credenciales son inválidas.
    """
    usuario = await autenticar_usuario(
        request_body.alias,
        request_body.contra,
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    # Payload del JWT según el requerimiento:
    #   id_usuario, alias, rol (nombre), scopes (array "recurso:accion").
    token_payload = {
        "id_usuario": usuario["id_usuario"],
        "alias": usuario["alias"],
        "rol": usuario["rol"],
        "scopes": usuario["scopes"],
    }
    token = crear_token_acceso(data=token_payload)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id_usuario": usuario["id_usuario"],
            "alias": usuario["alias"],
            "rol": usuario["rol"],
        },
        "scopes": usuario["scopes"],
    }


# ---------------------------------------------------------------------------
# Ejemplos de rutas protegidas con checkScope
# ---------------------------------------------------------------------------

@router.get(
    "/ventas",
    dependencies=[Depends(checkScope("ventas:leer"))],
    summary="Obtener ventas (protegida)",
    description="Ejemplo de ruta CRUD estándar protegida por el scope 'ventas:leer'.",
)
async def obtener_ventas():
    """Ruta de ejemplo que requiere el scope ``ventas:leer``."""
    # En producción, aquí se llamaría al servicio de ventas.
    return {"message": "Listado de ventas para usuarios con scope 'ventas:leer'"}


@router.post(
    "/ventas/{id}/anular",
    dependencies=[Depends(checkScope("ventas_anular:eliminar"))],
    summary="Anular venta (protegida)",
    description=(
        "Ejemplo de ruta de operación específica protegida por el scope "
        "'ventas_anular:eliminar'."
    ),
)
async def anular_venta(id: int):
    """Ruta de ejemplo que requiere el scope ``ventas_anular:eliminar``."""
    # En producción, aquí se llamaría al servicio que anula la venta.
    return {"message": f"Venta con id {id} anulada con éxito"}
