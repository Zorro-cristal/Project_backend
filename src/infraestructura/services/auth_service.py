"""Servicio de autenticación y construcción de scopes JWT.

Este módulo centraliza la lógica de:
1. Transformar la matriz RBAC (permisos_roles) en una lista plana de
   scopes con sintaxis ``"recurso:accion"``.
2. Autenticar un usuario (alias + contraseña) y devolver su información
   enriquecida con el rol y sus scopes.

La arquitectura sigue el patrón del proyecto (repositories + services),
reutilizando las funciones ya existentes para no duplicar lógica.
"""

from typing import Optional

from src.infraestructura.repositories.permiso_rol_repository import \
    obtenerPermisosPorRol
from src.infraestructura.repositories.usuario_repository import obtenerUsuarios
from src.infraestructura.services.rol_service import obtener_roles
from src.shared.security.password_hasher import verify_password
from src.shell.utils import attach_related

# Acciones disponibles en la tabla `permisos_roles` (columnas booleanas).
# El orden es irrelevante para la transformación, pero se mantiene para
# documentar que estas son las únicas acciones que se traducen a scopes.
ACCIONES = ("crear", "editar", "eliminar", "leer")


def construir_scopes_desde_permisos(permisos: list[dict]) -> list[str]:
    """Convierte la matriz de permisos en una lista plana de scopes.

    Recorre cada registro de ``permisos_roles`` (que ya debe traer el
    permiso relacionado embebido en ``permisos``) y produce cadenas con el
    formato ``"recurso:accion"`` (ej. ``"ventas:leer"``).

    Reglas:
    - Solo se incluyen los permisos cuyo estado sea ``1`` (activo).
    - Para cada recurso, se incluyen únicamente las acciones cuya columna
      booleana sea verdaderamente ``1`` / ``True``.

    Args:
        permisos: Lista de diccionarios de ``permisos_roles`` con la forma
            ``{crear, editar, eliminar, leer, id_permisofk, id_rolfk,
            permisos: {nombre, estado}}``.

    Returns:
        Lista plana de cadenas ``"recurso:accion"``.
    """
    scopes: list[str] = []

    for registro in permisos or []:
        # El permiso relacionado viene embebido en la clave `permisos`.
        permiso = registro.get("permisos") or {}
        # Solo permisos activos (estado == 1).
        if permiso.get("estado") != 1:
            continue

        recurso = permiso.get("nombre")
        if not recurso:
            continue

        # Solo incluye las acciones cuya columna sea verdadera (1 o True).
        for accion in ACCIONES:
            if registro.get(accion) is True or registro.get(accion) == 1:
                scopes.append(f"{recurso}:{accion}")

    return scopes


async def _obtener_permisos_del_rol(id_rol: int) -> list[dict]:
    """Obtiene los permisos activos (estado == 1) asignados a un rol.

    Args:
        id_rol: ID del rol del que se quieren los permisos.

    Returns:
        Lista de registros de ``permisos_roles`` con el permiso embebido.
    """
    registros = await obtenerPermisosPorRol(id_rol)
    return [
        r
        for r in registros
        if r.get("permisos") is not None
        and r.get("permisos", {}).get("estado") == 1
    ]


async def autenticar_usuario(alias: str, contra: str) -> Optional[dict]:
    """Valida credenciales y devuelve la información del usuario autenticado.

    El flujo es:
    1. Busca al usuario por ``alias`` (nunca por contraseña en texto plano).
    2. Verifica la contraseña ingresada contra el hash almacenado.
    3. Adjunta el rol del usuario (``roles``).
    4. Obtiene los permisos del rol (solo ``estado == 1``).
    5. Construye los scopes planos ``"recurso:accion"``.
    6. Sanitiza la respuesta para no exponer la contraseña.

    Args:
        alias: Alias del usuario.
        contra: Contraseña en texto plano.

    Returns:
        Un diccionario con ``{id, alias, rol, permisos, scopes, ...}`` o
        ``None`` si las credenciales son inválidas o el usuario no existe.
    """
    filtro = {"alias": alias}
    result = await obtenerUsuarios(filtro, 1, 0)

    if not result:
        return None

    usuario_db = result[0]
    contra_db = usuario_db.get("contra")
    if not contra_db:
        return None

    if not verify_password(contra, contra_db):
        return None

    # Adjuntar el rol del usuario (tabla `roles`).
    result = await attach_related(
        result,
        "id_rolfk",
        obtener_roles,
        "id",
        "id",
        "rol",
    )

    usuario = result[0]

    # Obtener permisos activos del rol y construir los scopes.
    id_rol = usuario_db.get("id_rolfk")
    permisos = await _obtener_permisos_del_rol(id_rol) if id_rol else []
    scopes = construir_scopes_desde_permisos(permisos)

    # Sanitizar: nunca devolver la contraseña al cliente.
    usuario.pop("contra", None)

    # Exponer la estructura final usada por el endpoint de login.
    return {
        "id_usuario": usuario.get("id"),
        "alias": usuario.get("alias"),
        "rol": (usuario.get("rol") or {}).get("nombre"),
        "permisos": permisos,
        "scopes": scopes,
    }
