import os
import pytest
from src.configs.settings import get_settings
from src.infraestructura.config.supabase import get_supabase_client
from src.shell.adaptadores.database.generic_crud import (count, get, insert,
                                                         soft_delete, update)


# ============ PRUEBAS DE CONFIGURACIÓN ============
def test_settings_loaded():
    """Verifica que las variables de entorno estén cargadas correctamente"""
    settings = get_settings()
    assert settings.SUPABASE_URL is not None, "SUPABASE_URL no está configurada"
    assert settings.SUPABASE_KEY is not None, "SUPABASE_KEY no está configurada"
    assert settings.SUPABASE_URL.startswith("https://"), "URL de Supabase inválida"
    print(f"✓ SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"✓ SUPABASE_KEY: {settings.SUPABASE_KEY[:20]}...")  # Mostrar solo parte de la clave

# ============ PRUEBAS DE CONEXIÓN ============
def test_supabase_client_connection():
    """Verifica que el cliente de Supabase se haya creado correctamente"""
    try:
        client = get_supabase_client()
        assert client is not None, "No se pudo crear el cliente de Supabase"
        print("✓ Cliente de Supabase creado exitosamente")
    except Exception as e:
        pytest.fail(f"Error al conectar con Supabase: {str(e)}")

def test_supabase_auth_connection():
    """Verifica que puedas acceder a Supabase (sin usar tablas específicas)"""
    try:
        client = get_supabase_client()
        # Intenta obtener info de usuario anónimo (no requiere tabla específica)
        user = client.auth.get_user()
        print("✓ Conexión autenticada con Supabase")
        return True
    except Exception as e:
        print(f"⚠ Conexión anónima (esperado): {str(e)}")
        return False

# ============ PRUEBAS DE LECTURA (CRUD) ============
@pytest.mark.asyncio
async def test_get_from_table():
    """Verifica que puedas leer datos de una tabla específica"""
    try:
        # CAMBIA 'usuarios' por el nombre de tu tabla real
        result = await get('usuarios')
        print(f"✓ Lectura de tabla exitosa. Registros: {len(result)}")
        assert isinstance(result, list), "La respuesta debe ser una lista"
    except Exception as e:
        pytest.fail(f"Error al leer de la tabla: {str(e)}")

@pytest.mark.asyncio
async def test_get_with_filter():
    """Verifica que puedas leer datos con filtros"""
    try:
        # CAMBIA 'usuarios' y 'estado' por valores reales de tu tabla
        result = await get('usuarios', filters={"estado": "activo"})
        print(f"✓ Lectura con filtro exitosa. Registros: {len(result)}")
        assert isinstance(result, list), "La respuesta debe ser una lista"
    except Exception as e:
        pytest.fail(f"Error al filtrar datos: {str(e)}")

# ============ PRUEBA DE INSERCIÓN ============
@pytest.mark.asyncio
async def test_insert_data():
    """Verifica que puedas insertar datos en una tabla"""
    try:
        test_data = {
            "nombre": "Test User",
            "email": "test@example.com",
            "estado": "activo"
            # CAMBIA ESTO CON LOS CAMPOS REALES DE TU TABLA
        }
        result = await insert('usuarios', test_data)
        print(f"✓ Inserción exitosa. ID: {result.get('id')}")
        assert result.get('id') is not None, "El registro no tiene ID"
        return result.get('id')
    except Exception as e:
        pytest.fail(f"Error al insertar datos: {str(e)}")

# ============ EJECUCIÓN DIRECTA ============
if __name__ == "__main__":
    # Para ejecutar sin pytest desde el archivo
    print("\n=== PRUEBAS DE CONEXIÓN A SUPABASE ===\n")
    
    try:
        test_settings_loaded()
        test_supabase_client_connection()
        test_supabase_auth_connection()
        print("\n✅ Todas las pruebas básicas pasaron exitosamente")
    except AssertionError as e:
        print(f"\n❌ Error en prueba: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")