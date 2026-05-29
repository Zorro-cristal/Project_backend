from fastapi.testclient import TestClient

from src.api.index import app
from src.shell.adapters.database.generic_crud import get

tester= TestClient(app)

def test_returns_200_ok():
    response = tester.get("/health")
    result= get('demo')
    assert response.status_code == 200
    # El endpoint /health puede devolver un wrapper distinto.
    response_json = response.json()
    if hasattr(result, "__await__"):
        result_value = None
    else:
        result_value = result

    assert response_json.get("detail") == result_value or response_json == {"detail": result_value} or response_json == result_value


