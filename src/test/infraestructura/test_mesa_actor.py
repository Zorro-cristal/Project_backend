import asyncio

from src.infraestructura.api import mesa_api
from src.shell.adapters.requests.mesa_request import MesaRequest, MesaUpdateRequest


def test_crear_mesa_usa_el_usuario_autenticado(monkeypatch):
    captured_payload = {}

    async def fake_crear_mesa(payload):
        captured_payload.update(payload)
        return payload

    monkeypatch.setattr(mesa_api, "crear_mesa", fake_crear_mesa)

    response = asyncio.run(
        mesa_api.agregarMesaApi(
            MesaRequest(nombre="Mesa 5", capacidad=4, id_localfk=1),
            current_user={"id": 27},
        )
    )

    assert response["message"]["actualizado_por"] == 27
    assert captured_payload["actualizado_por"] == 27


def test_actualizar_mesa_usa_el_usuario_autenticado(monkeypatch):
    captured_payload = {}
    captured_ids = []

    async def fake_actualizar_mesa(id, payload):
        captured_ids.append(id)
        captured_payload.update(payload)
        return payload

    monkeypatch.setattr(mesa_api, "actualizar_mesa", fake_actualizar_mesa)

    response = asyncio.run(
        mesa_api.actualizarMesaApi(
            5,
            MesaUpdateRequest(nombre="Mesa actualizada"),
            current_user={"id": 28},
        )
    )

    assert response["message"]["actualizado_por"] == 28
    assert captured_payload["actualizado_por"] == 28
    assert captured_ids == [5]


def test_patch_mesa_usa_el_usuario_autenticado(monkeypatch):
    captured_payload = {}
    captured_ids = []

    async def fake_actualizar_mesa(id, payload):
        captured_ids.append(id)
        captured_payload.update(payload)
        return payload

    monkeypatch.setattr(mesa_api, "actualizar_mesa", fake_actualizar_mesa)

    response = asyncio.run(
        mesa_api.patchMesaApi(
            5,
            MesaUpdateRequest(estado=0),
            current_user={"id": 29},
        )
    )

    assert response["message"]["actualizado_por"] == 29
    assert captured_payload["actualizado_por"] == 29
    assert captured_ids == [5]
