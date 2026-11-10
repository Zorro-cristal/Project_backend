from datetime import datetime, timedelta, timezone

from src.infraestructura.config.turso import get_turso_connection
from src.shell.adapters.database.generic_crud import insert


async def get_login_attempts(ip: str, alias: str, window_minutes: int = 15) -> dict[str, int]:
    """Cuenta fallos recientes para aplicar el límite por IP y alias."""
    since = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
    connection = get_turso_connection()
    try:
        cursor = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM audit_login
            WHERE ip = ? AND alias = ? AND resultado IN ('fail', 'inactive')
              AND datetime(fecha) >= datetime(?)
              AND fecha > COALESCE(
                  (
                      SELECT MAX(fecha)
                      FROM audit_login
                      WHERE ip = ? AND alias = ? AND resultado = 'success'
                  ),
                  ''
              )
            """,
            (ip, alias, since, ip, alias),
        )
        row = cursor.fetchone()
        return {"count": int(row[0]) if row else 0}
    finally:
        connection.close()

async def register_login_event(data: dict) -> dict:
    """Registra un evento de intento de login en la tabla audit_login."""
    try:
        return await insert("audit_login", data)
    except Exception as exc:
        raise RuntimeError("No se pudo registrar el evento de auditoría del login.") from exc