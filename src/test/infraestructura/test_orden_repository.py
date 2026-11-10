import asyncio
import sqlite3

from src.infraestructura.repositories import orden_repository
from src.shell.adapters.database import generic_crud


def test_obtener_orden_preserves_order_fields_when_mesa_has_same_column_names(monkeypatch):
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.execute(
        "CREATE TABLE ordenes (id INTEGER, estado INTEGER, id_mesafk INTEGER, "
        "id_clientefk INTEGER, cantidad INTEGER)"
    )
    connection.execute(
        "CREATE TABLE mesas (id INTEGER, nombre TEXT, estado INTEGER, capacidad INTEGER, "
        "id_localfk INTEGER, id_clientefk INTEGER, ocupado_desde TEXT)"
    )
    connection.execute(
        "INSERT INTO ordenes (id, estado, id_mesafk, id_clientefk, cantidad) "
        "VALUES (42, 1, 9, 4, 2)"
    )
    connection.execute(
        "INSERT INTO mesas "
        "(id, nombre, estado, capacidad, id_localfk, id_clientefk, ocupado_desde) "
        "VALUES (9, 'Mesa 9', 2, 4, 3, 5, '10:00:00')"
    )
    monkeypatch.setattr(generic_crud, "get_turso_connection", lambda: connection)

    ordenes = asyncio.run(orden_repository.obtenerOrdenes(filtros={"id_mesafk": 9}))

    assert ordenes[0]["id"] == 42
    assert ordenes[0]["estado"] == 1
    assert ordenes[0]["id_clientefk"] == 4
    assert "nombre" not in ordenes[0]
    assert ordenes[0]["mesas"] == {
        "id": 9,
        "nombre": "Mesa 9",
        "capacidad": 4,
        "id_localfk": 3,
        "ocupado_desde": "10:00:00",
    }
