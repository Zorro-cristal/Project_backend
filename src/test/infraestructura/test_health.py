from fastapi.testclient import TestClient

from src.api.index import app
from src.shell.flujo.prueba import conexion_supabase as healthcheck

tester = TestClient(app)


class DummyCursor:
    def fetchone(self):
        return (1,)


class DummyConnection:
    def execute(self, _query: str):
        return DummyCursor()

    def close(self):
        pass


def test_returns_200_ok(monkeypatch):
    monkeypatch.setattr(
        healthcheck,
        "get_turso_connection",
        lambda: DummyConnection(),
        raising=False,
    )
    response = tester.get("/health")
    assert response.status_code == 200
    assert response.json()["conexion"] is True


