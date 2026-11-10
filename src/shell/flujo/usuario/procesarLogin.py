from datetime import datetime, timezone
from uuid import uuid4

from src.infraestructura.models.usuario import Usuario
from src.infraestructura.repositories.login_attempt_repository import (
    get_login_attempts, register_login_event)
from src.infraestructura.repositories.usuario_repository import obtenerUsuarios
from src.infraestructura.services.rol_service import obtener_roles
from src.shared.security.password_hasher import verify_password
from src.shared.utils.security_utils import get_client_ip, normalize_alias
from src.shell.utils import attach_related

MAX_LOGIN_ATTEMPTS = 5
MAX_USER_AGENT_LENGTH = 512
MAX_ALIAS_LENGTH = 255
MAX_REQUEST_ID_LENGTH = 128


def _login_audit_data(
    alias: str,
    ip: str,
    user_agent: str,
    request_id: str,
    resultado: str,
    motivo: str,
    usuario_id: int | None = None,
) -> dict:
    return {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "alias": alias[:MAX_ALIAS_LENGTH],
        "usuario_id": usuario_id,
        "resultado": resultado,
        "motivo": motivo,
        "ip": ip,
        "user_agent": user_agent[:MAX_USER_AGENT_LENGTH] or None,
        "request_id": request_id[:MAX_REQUEST_ID_LENGTH],
    }


async def procesarLogin(usuario: Usuario, request=None):
    alias_normalizado = normalize_alias(usuario.alias)
    client_ip = get_client_ip(request)[:64] if request else "unknown"
    headers = getattr(request, "headers", {}) if request else {}
    user_agent = str(headers.get("user-agent", ""))[:MAX_USER_AGENT_LENGTH]
    request_id = str(headers.get("x-request-id") or uuid4())[:MAX_REQUEST_ID_LENGTH]

    if len(alias_normalizado) > MAX_ALIAS_LENGTH:
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "fail",
                "invalid_alias",
            )
        )
        return []

    attempts = await get_login_attempts(client_ip, alias_normalizado)
    if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "blocked",
                "rate_limited",
            )
        )
        return []

    result = await obtenerUsuarios({"alias": alias_normalizado}, 1, 0)
    if not result:
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "fail",
                "unknown_user",
            )
        )
        return []

    usuario_db = result[0]
    usuario_id = usuario_db.get("id")
    if usuario_db.get("estado") != 1:
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "inactive",
                "inactive_user",
                usuario_id,
            )
        )
        return []

    contra_db = usuario_db.get("contra")
    if not contra_db or not verify_password(usuario.contra, contra_db):
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "fail",
                "invalid_credentials",
                usuario_id,
            )
        )
        return []

    result = await attach_related(
        result,
        "id_rolfk",
        obtener_roles,
        "id",
        "id",
        "rol",
    )
    rol = result[0].get("rol")
    if not rol or rol.get("estado") != 1:
        await register_login_event(
            _login_audit_data(
                alias_normalizado,
                client_ip,
                user_agent,
                request_id,
                "inactive",
                "inactive_role",
                usuario_id,
            )
        )
        return []

    result[0]["permisos"] = rol.get("permisos", [])
    result[0].pop("contra", None)

    await register_login_event(
        _login_audit_data(
            alias_normalizado,
            client_ip,
            user_agent,
            request_id,
            "success",
            "authenticated",
            usuario_id,
        )
    )
    return result
