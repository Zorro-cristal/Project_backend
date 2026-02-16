from fastapi.testclient import TestClient
from src.api.index import app
from src.shell.adaptadores.database.generic_crud import get

tester= TestClient(app)

def test_returns_200_ok():
    response = tester.get("/health")
    result= get('demo')
    assert response.status_code == 200
    assert response.json() == {"detail": result}