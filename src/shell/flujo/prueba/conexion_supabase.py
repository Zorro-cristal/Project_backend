import httpx

from src.configs.settings import get_settings
from src.infraestructura.config.supabase import get_supabase_client
from src.shell.adaptadores.database.generic_crud import get


async def conexion_supabase(verificar_autenticacion: bool = False, tabla_prueba: str = "demo") -> dict:
    """Prueba de conexión a Supabase sin depender de tablas.

    - Realiza una petición GET al endpoint de una tabla específica con limit=0
      para verificar que el servicio responde y es accesible con la API key.
    - Si `verificar_autenticacion=True`, intenta una comprobación ligera de autenticación
      usando `cliente.auth.get_user()` (puede devolver error si no hay sesión).

    Retorna un dict con keys: `conexion` (bool), `codigo_estado` (int|None),
    `autenticacion_exitosa` (bool|None) y `mensaje`.
    """
    configuracion = get_settings()
    url = f"{configuracion.SUPABASE_URL.rstrip('/')}/rest/v1/{tabla_prueba}?limit=0"
    encabezados = {
        "apikey": configuracion.SUPABASE_KEY,
        "Authorization": f"Bearer {configuracion.SUPABASE_KEY}",
        "Accept": "application/json",
    }

    resultado = {
        "conexion": False,
        "codigo_estado": None,
        "autenticacion_exitosa": None,
        "mensaje": "",
    }

    # Comprobar el endpoint REST con GET ligero (limit=0)
    try:
        async with httpx.AsyncClient(timeout=5.0) as cliente:
            respuesta = await cliente.get(url, headers=encabezados, follow_redirects=True)
            resultado["codigo_estado"] = respuesta.status_code
            
            if 200 <= respuesta.status_code < 300:
                # Códigos 2xx = conexión exitosa
                resultado["conexion"] = True
                resultado["mensaje"] = f"Endpoint REST alcanzable en tabla '{tabla_prueba}' (estado {respuesta.status_code})"
            elif respuesta.status_code == 401:
                # 401 = Unauthorized, problema con API key
                resultado["conexion"] = False
                resultado["mensaje"] = f"Error de autenticación: API key inválida o expirada (estado {respuesta.status_code})"
            elif respuesta.status_code == 403:
                # 403 = Forbidden, problema de permisos
                resultado["conexion"] = False
                resultado["mensaje"] = f"Error de permisos: API key sin permisos suficientes (estado {respuesta.status_code})"
            elif 400 <= respuesta.status_code < 500:
                # Otros 4xx = cliente error
                resultado["conexion"] = False
                resultado["mensaje"] = f"Error del cliente en endpoint REST (estado {respuesta.status_code}). Verifica que la tabla '{tabla_prueba}' existe."
            else:
                # 5xx = error del servidor
                resultado["conexion"] = False
                resultado["mensaje"] = f"Error del servidor en endpoint REST (estado {respuesta.status_code})"
    except Exception as e:
        resultado["conexion"] = False
        resultado["mensaje"] = f"Error al contactar endpoint REST: {str(e)}"

    # Opcional: comprobar autenticación ligera usando el cliente oficial
    if verificar_autenticacion and resultado["conexion"]:
        try:
            cliente_supabase = get_supabase_client()
            # `auth.get_user()` puede lanzar si no hay sesión; capturamos y devolvemos False
            try:
                _ = cliente_supabase.auth.get_user()
                resultado["autenticacion_exitosa"] = True
                resultado["mensaje"] += "; verificación de autenticación exitosa"
            except Exception:
                resultado["autenticacion_exitosa"] = False
                resultado["mensaje"] += "; verificación de autenticación falló o no hay sesión activa"
        except Exception as e:
            resultado["autenticacion_exitosa"] = False
            resultado["mensaje"] += f"; error al crear cliente supabase: {str(e)}"

    test= await get('demo')
    print(test)
    return resultado
    return resultado
