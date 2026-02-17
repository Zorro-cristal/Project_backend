from fastapi import APIRouter

from src.shell.flujo.prueba.test import test_settings_loaded, test_supabase_auth_connection, test_supabase_client_connection
from src.shell.adaptadores.database.generic_crud import get

router = APIRouter()

@router.get("/health")
async def read_root():
    result = await get('demo')
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
    return {"detail": result}

@router.get("/")
async def read_root2():
    return {"detail": "hello world"}