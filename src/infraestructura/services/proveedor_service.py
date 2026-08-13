from src.shell.utils import attach_related, filtrar_por_nombre_completo

from ..models.proveedor import Proveedor
from ..repositories.proveedor_repository import (actualizarProveedor,
                                                 obtenerProveedor)
from .persona_service import (actualizar_persona, crear_persona,
                              obtener_personas)


def build_proveedor_entity(payload: dict) -> Proveedor:
    valid_fields = {key: value for key, value in payload.items() if key in Proveedor.__annotations__}
    return Proveedor(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_proveedores(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    filtros = dict(filtros or {})
    nombre_completo = filtros.pop("nombre_completo", None)
    proveedores = await obtenerProveedor(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    if not proveedores:
        return proveedores
    proveedores = await attach_related(proveedores, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'persona')
    if nombre_completo:
        proveedores = filtrar_por_nombre_completo(proveedores, nombre_completo, path=['persona'])
    return proveedores


async def crear_proveedor(payload: dict):
    proveedor = build_proveedor_entity(payload)
    return await actualizarProveedor(proveedor)


async def actualizar_proveedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarProveedor(payload, id)
