"""Ejemplos de rutas protegidas por scopes.

Contiene:
1. Ejemplos de rutas protegidas con ``checkScope``:
   - ``GET /ventas`` → requiere ``ventas:leer``.
   - ``POST /ventas/{id}/anular`` → requiere ``ventas_anular:eliminar``.
"""

from fastapi import APIRouter, Depends

from src.shared.security.scopes import checkScope

router = APIRouter()


# ---------------------------------------------------------------------------
# Ejemplos de rutas protegidas con checkScope
# ---------------------------------------------------------------------------

@router.get(
    "/ventas",
    dependencies=[Depends(checkScope("ventas:leer"))],
    summary="Obtener ventas (protegida)",
    description="Ejemplo de ruta CRUD estándar protegida por el scope 'ventas:leer'.",
)
async def obtener_ventas():
    """Ruta de ejemplo que requiere el scope ``ventas:leer``."""
    # En producción, aquí se llamaría al servicio de ventas.
    return {"message": "Listado de ventas para usuarios con scope 'ventas:leer'"}


@router.post(
    "/ventas/{id}/anular",
    dependencies=[Depends(checkScope("ventas_anular:eliminar"))],
    summary="Anular venta (protegida)",
    description=(
        "Ejemplo de ruta de operación específica protegida por el scope "
        "'ventas_anular:eliminar'."
    ),
)
async def anular_venta(id: int):
    """Ruta de ejemplo que requiere el scope ``ventas_anular:eliminar``."""
    # En producción, aquí se llamaría al servicio que anula la venta.
    return {"message": f"Venta con id {id} anulada con éxito"}
