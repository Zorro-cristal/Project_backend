import asyncio
import sqlite3

from src.infraestructura.repositories import mesa_repository
from src.shell.adapters.database import generic_crud


def test_obtener_mesa_preserves_mesa_name_and_id(monkeypatch):
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.execute(
        "CREATE TABLE mesas (id INTEGER, nombre TEXT, id_localfk INTEGER)"
    )
    connection.execute(
        "CREATE TABLE locales (id INTEGER, nombre TEXT, direccion TEXT)"
    )
    connection.execute(
        "INSERT INTO mesas (id, nombre, id_localfk) VALUES (7, 'Mesa 7', 1)"
    )
    connection.execute(
        "INSERT INTO locales (id, nombre, direccion) VALUES (1, 'Local Uno', 'Calle 1')"
    )
    monkeypatch.setattr(generic_crud, "get_turso_connection", lambda: connection)

    mesas = asyncio.run(mesa_repository.obtenerMesa())

    assert mesas[0]["id"] == 7
    assert mesas[0]["nombre"] == "Mesa 7"
    assert mesas[0]["locales"] == {
        "id": 1,
        "nombre": "Local Uno",
        "direccion": "Calle 1",
    }
