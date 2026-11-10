from fastapi.testclient import TestClient

from src.api.index import app, fastapi_app, origins

ALLOWED_ORIGIN = origins[0]
tester = TestClient(app, raise_server_exceptions=False)


async def fail_request():
    raise RuntimeError("CORS test error")


fastapi_app.add_api_route("/__cors_test_error__", fail_request, methods=["GET"])


def test_preflight_returns_cors_headers_for_allowed_origin():
    response = tester.options(
        "/proveedor/",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert response.headers["access-control-max-age"] == "14400"


def test_preflight_rejects_unconfigured_origin():
    response = tester.options(
        "/proveedor/",
        headers={
            "Origin": "https://unconfigured.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_cors_headers_are_present_on_server_errors():
    response = tester.get(
        "/__cors_test_error__",
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
