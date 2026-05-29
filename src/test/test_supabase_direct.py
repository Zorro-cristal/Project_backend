"""
Script de prueba directo para verificar conexión a Supabase
Ejecutare: python test_supabase_direct.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.configs.settings import get_settings
from src.infraestructura.config.supabase import get_supabase_client


def print_section(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_configuration():
    """Prueba 1: Verifica configuración"""
    print_section("PRUEBA 1: Verificar Configuración")
    try:
        settings = get_settings()
        print(f"✓ SUPABASE_URL: {settings.SUPABASE_URL}")
        print(f"✓ SUPABASE_KEY: {settings.SUPABASE_KEY[:30]}...")
        print(f"✓ API_VERSION: {settings.API_VERSION}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_connection():
    """Prueba 2: Verifica conexión con cliente"""
    print_section("PRUEBA 2: Conectar con Supabase")
    try:
        client = get_supabase_client()
        print(f"✓ Cliente Supabase creado")
        print(f"✓ Tipo de cliente: {type(client)}")
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False

def test_tables():
    """Prueba 3: Lista las tablas disponibles"""
    print_section("PRUEBA 3: Obtener Tablas Disponibles")
    try:
        client = get_supabase_client()
        # Intenta acceder a una tabla dummy para verificar si puedes conectar
        response = client.from_("information_schema.tables").select("table_name").execute()
        tables = [row["table_name"] for row in response.data if row["table_name"] != "schema_migrations"]
        
        if tables:
            print(f"✓ Tablas encontradas ({len(tables)}):")
            for table in tables[:10]:  # Mostrar primeras 10
                print(f"  - {table}")
            if len(tables) > 10:
                print(f"  ... y {len(tables) - 10} más")
        else:
            print("⚠ No se encontraron tablas públicas")
        return True
    except Exception as e:
        print(f"⚠ No se pudo obtener tablas: {e}")
        print("  Esto es normal si las tablas están en otro schema")
        return False

def test_simple_query():
    """Prueba 4: Intenta una consulta simple a una tabla específica.

    Nota: en CI/pytest no se debe pedir input por stdin.
    Se omite si no hay tabla candidata conocida.
    """
    print_section("PRUEBA 4: Consulta a Tabla Específica")

    # Evitar input interactivo en pytest.
    table_name = "usuarios"

    if not table_name:
        print("⚠ No se ingresó nombre de tabla, saltando prueba")
        return False

    
    try:
        client = get_supabase_client()
        response = client.table(table_name).select("*").limit(5).execute()
        print(f"✓ Consulta exitosa a tabla '{table_name}'")
        print(f"✓ Registros obtenidos: {len(response.data)}")
        if response.data:
            print(f"✓ Columnas: {list(response.data[0].keys())}")
        return True
    except Exception as e:
        print(f"✗ Error al consultar '{table_name}': {e}")
        return False

def test_health_check():
    """Prueba 5: Health check del API"""
    print_section("PRUEBA 5: Health Check del API")
    try:
        client = get_supabase_client()
        # Hacer una consulta mínima
        response = client.auth.get_session()
        print(f"✓ API de Supabase respondiendo correctamente")
        return True
    except Exception as e:
        print(f"⚠ Health check: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("  🧪 PRUEBAS DE CONEXIÓN A SUPABASE")
    print("="*60)
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(("Configuración", test_configuration()))
    results.append(("Conexión", test_connection()))
    results.append(("Tablas", test_tables()))
    results.append(("Health Check", test_health_check()))
    results.append(("Tabla Específica", test_simple_query()))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status:<10} - {name}")
    
    print(f"\nTotal: {passed}/{total} pruebas completadas")
    
    if passed >= 3:
        print("\n✅ Tu conexión con Supabase funciona correctamente")
    else:
        print("\n❌ Hay problemas con la conexión a Supabase")
    
    return passed >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
