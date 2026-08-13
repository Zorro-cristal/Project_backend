import pytest
from fastapi.testclient import TestClient

from src.api.index import app

# Inicializa el cliente de prueba
client = TestClient(app)

# Obtiene el token
@pytest.fixture(scope="session")
def auth_token():
    # Simula login para obtener el token
    response = client.post("/usuario/login", json={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()
    # Ajusta la clave según tu backend (ej: "access_token")
    return data["access_token"]

def test_get_usuarios(auth_token, limit=5, offset=0):
    response = client.get(
        "/usuario",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_productos(auth_token, limit=10, offset=0):
    response = client.get(
        "/productos",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_categorias(auth_token, limit=3, offset=0):
    response = client.get(
        "/categorias",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_marcas(auth_token, limit=4, offset=0):
    response = client.get(
        "/marcas",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_precios(auth_token, limit=6, offset=0):
    response = client.get(
        "/precios",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_ingredientes(auth_token, limit=8, offset=0):
    response = client.get(
        "/ingredientes",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_rol(auth_token, limit=5, offset=0):
    response = client.get(
        "/roles",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_roles(auth_token, limit=5, offset=3):
    response = client.get(
        "/rol",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_producto(auth_token, limit=10, offset=0):
    response = client.get(
        "/producto",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_permisos(auth_token, limit=7, offset=1):
    response = client.get(
        "/permiso",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_detalles_producto(auth_token, limit=5, offset=0):
    response = client.get(
        "/detalles_producto",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_clientes(auth_token, limit=5, offset=0):
    response = client.get(
        "/cliente",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit
    
def test_get_personas(auth_token, limit=5, offset=0):
    response = client.get(
        "/persona",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= limit

# Pruebas adicionales para otros endpoints según sea necesario
def test_get_proveedor(auth_token, limit=5, offset=0):
    response = client.get(
        "/proveedor",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_local(auth_token, limit=5, offset=0):
    response = client.get(
        "/local",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_vendedor(auth_token, limit=5, offset=0):
    response = client.get(
        "/vendedor",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_mesa(auth_token, limit=5, offset=0):
    response = client.get(
        "/mesa",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_stock(auth_token, limit=5, offset=0):
    response = client.get(
        "/stock",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_caja(auth_token, limit=5, offset=0):
    response = client.get(
        "/caja",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_venta(auth_token, limit=5, offset=0):
    response = client.get(
        "/venta",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_detalle_venta(auth_token, limit=5, offset=0):
    response = client.get(
        "/detalle_venta",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_timbrado(auth_token, limit=5, offset=0):
    response = client.get(
        "/timbrado",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_egreso(auth_token, limit=5, offset=0):
    response = client.get(
        "/egreso",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_compra(auth_token, limit=5, offset=0):
    response = client.get(
        "/compra",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_detalle_compra(auth_token, limit=5, offset=0):
    response = client.get(
        "/detalle_compra",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_orden(auth_token, limit=5, offset=0):
    response = client.get(
        "/orden",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_cuota_venta(auth_token, limit=5, offset=0):
    response = client.get(
        "/cuota_venta",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_pago_venta(auth_token, limit=5, offset=0):
    response = client.get(
        "/pago_venta",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_cuota_compra(auth_token, limit=5, offset=0):
    response = client.get(
        "/cuota_compra",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

def test_get_pago_compra(auth_token, limit=5, offset=0):
    response = client.get(
        "/pago_compra",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data

if __name__ == "__main__":
    pytest.main(["-v", "src/test/infraestructura/test_endpoints_get.py"])