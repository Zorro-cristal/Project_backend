from src.shell.utils import attach_related, filtrar_por_nombre_completo

from ..models.vendedor import Vendedor
from ..repositories.vendedor_repository import (actualizarVendedor,
                                                obtenerVendedor)
from .usuario_service import obtener_usuarios_sin_rol


def build_vendedor_entity(payload: dict) -> Vendedor:
    valid_fields = {key: value for key, value in payload.items() if key in Vendedor.__annotations__}
    return Vendedor(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_vendedores(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    filtros = dict(filtros or {})
    vendedores = await obtenerVendedor(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    return vendedores


async def crear_vendedor(payload: dict):
    vendedor = build_vendedor_entity(payload)
    return await actualizarVendedor(vendedor)


async def actualizar_vendedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarVendedor(payload, id)
