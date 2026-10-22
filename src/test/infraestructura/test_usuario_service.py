import asyncio

import pytest

from src.infraestructura.services import usuario_service
from src.shell.adapters.requests.usuario_request import UsuarioRequest


def test_crear_usuario_crea_persona_recibida_con_alias_plural(monkeypatch):
    payload = UsuarioRequest.model_validate(
        {
            "id": 0,
            "contra": "test",
            "alias": "test",
            "estado": True,
            "fecha_creado": "2026-10-20T18:41:21.108Z",
            "id_rolfk": 2,
            "id_personafk": 123,
            "personas": {
                "cedula": 123,
                "nombres": "test",
                "apellidos": "test",
            },
        }
    ).model_dump()
    creada = []
    monkeypatch.setattr(usuario_service, "obtenerRol", _async_result([{"id": 2}]))
    monkeypatch.setattr(usuario_service, "obtener_personas", _async_result([]))
    monkeypatch.setattr(
        usuario_service,
        "crear_persona",
        _async_result({"cedula": 123}),
    )
    monkeypatch.setattr(usuario_service, "_hash_if_needed", lambda data: data)
    monkeypatch.setattr(
        usuario_service,
        "actualizarUsuario",
        _async_capture(creada),
    )

    asyncio.run(usuario_service.crear_usuario(payload))

    assert creada[0].id_personafk == 123
    assert creada[0].id_rolfk == 2
    assert creada[0].personas is None


def test_crear_usuario_rechaza_rol_inexistente_antes_de_crear_persona(monkeypatch):
    persona_creada = []
    monkeypatch.setattr(usuario_service, "obtenerRol", _async_result([]))
    monkeypatch.setattr(
        usuario_service,
        "crear_persona",
        _async_capture(persona_creada),
    )

    with pytest.raises(ValueError, match="El rol con id 2 no existe"):
        asyncio.run(
            usuario_service.crear_usuario(
                {
                    "alias": "test",
                    "contra": "test",
                    "id_rolfk": 2,
                    "personas": {
                        "cedula": 123,
                        "nombres": "test",
                        "apellidos": "test",
                    },
                }
            )
        )

    assert persona_creada == []


def _async_result(result):
    async def return_result(*_args, **_kwargs):
        return result

    return return_result


def _async_capture(captured):
    async def capture(value, *_args, **_kwargs):
        captured.append(value)
        return value

    return capture
