"""Middleware / dependencia de autorización basada en scopes JWT.

Provee ``checkScope``, una dependencia reutilizable de FastAPI que:

1. Extrae y verifica el token JWT del encabezado ``Authorization: Bearer <token>``.
2. Extrae el array de ``scopes`` del payload del token.
3. Valida si el scope requerido está presente.
4. Si NO lo tiene, responde ``403 Forbidden`` con el mensaje
   ``{"message": "No tiene permisos suficientes para esta operación"}``.
5. Si SÍ lo tiene, permite el paso al controlador.

Uso típico:

    @router.get(
        "/ventas",
        dependencies=[Depends(checkScope("ventas:leer"))],
    )
    async def obtener_ventas():
        ...
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.security.auth_handler import decodificar_token

# Objeto reutilizable que extrae el esquema ``Authorization: Bearer <token>``.
security = HTTPBearer(auto_error=False)

# Mensaje estándar de respuesta cuando el usuario no tiene el scope.
MENSAJE_SIN_PERMISOS = "No tiene permisos suficientes para esta operación"


def _extraer_scopes_del_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> list[str]:
    """Extrae y valida el token JWT, devolviendo su lista de scopes.

    Args:
        credentials: Credenciales HTTP (o ``None`` si no se enviaron).

    Returns:
        Lista de scopes contenida en el payload del token.

    Raises:
        HTTPException(401): Si el token falta, es inválido o está expirado.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación no proporcionadas",
        )

    payload = decodificar_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    scopes = payload.get("scopes") or []
    if not isinstance(scopes, list):
        scopes = []

    return scopes


def checkScope(required_scope: str) -> Callable:
    """Crea una dependencia que valida que el usuario posea un scope.

    Args:
        required_scope: Scope obligatorio en formato ``"recurso:accion"``
            (ej. ``"ventas:leer"``).

    Returns:
        Una dependencia asíncrona de FastAPI que lanza un ``403 Forbidden``
        si el scope requerido no está presente en el token, o que permite el
        paso devolviendo el payload del usuario autenticado.
    """

    async def scope_dependency(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ):
        scopes = _extraer_scopes_del_token(credentials)

        if required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MENSAJE_SIN_PERMISOS,
            )

        # Devuelve el payload del token por si el controlador lo necesita.
        return decodificar_token(credentials.credentials)

    return scope_dependency
