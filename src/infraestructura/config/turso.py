"""Configuración de conexión HTTP a la base de datos Turso."""

from __future__ import annotations

from typing import Any

import libsql

from src.configs.settings import get_settings


def get_turso_connection() -> Any:
    """Crea una conexión remota a Turso usando variables de entorno.

    La conexión se crea por operación para evitar compartir conexiones HTTP entre
    ejecuciones concurrentes de FastAPI/Vercel.
    """
    settings = get_settings()
    database_url = settings.TURSO_DATABASE_URL
    auth_token = settings.TURSO_AUTH_TOKEN

    if not database_url or not auth_token:
        raise RuntimeError(
            "Configura TURSO_DATABASE_URL y TURSO_AUTH_TOKEN en el entorno."
        )

    return libsql.connect(database=database_url, auth_token=auth_token)
