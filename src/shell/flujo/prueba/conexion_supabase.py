import asyncio
from typing import Any

from src.infraestructura.config.turso import get_turso_connection


async def conexion_turso(verificar_autenticacion: bool = False) -> dict[str, Any]:
    """Comprueba Turso con una consulta mínima, sin acceder a una tabla de negocio."""
    del verificar_autenticacion  # La autenticación de BD se realiza con el token de Turso.

    def check_connection() -> None:
        connection = get_turso_connection()
        try:
            connection.execute("SELECT 1").fetchone()
        finally:
            connection.close()

    try:
        await asyncio.to_thread(check_connection)
        return {
            "conexion": True,
            "codigo_estado": None,
            "autenticacion_exitosa": None,
            "mensaje": "Conexión a Turso establecida.",
        }
    except Exception as error:
        return {
            "conexion": False,
            "codigo_estado": None,
            "autenticacion_exitosa": False,
            "mensaje": f"No se pudo conectar a Turso: {error}",
        }


async def conexion_supabase(
    verificar_autenticacion: bool = False,
    tabla_prueba: str | None = None,
) -> dict[str, Any]:
    """Alias temporal para los imports históricos del health check."""
    del tabla_prueba
    return await conexion_turso(verificar_autenticacion)
