from src.shell.utils import attach_related, filtrar_por_nombre_completo

from ..models.vendedor import Vendedor
from ..repositories.vendedor_repository import (actualizarVendedor,
                                                obtenerVendedor)
from .usuario_service import obtener_usuarios_sin_rol


def build_vendedor_entity(payload: dict) -> Vendedor:
    valid_fields = {key: value for key, value in payload.items() if key in Vendedor.__annotations__}
    return Vendedor(**valid_fields)


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_vendedores(filtros: dict = None, columnas: str = '*'):
    filtros = dict(filtros or {})
    nombre_completo = filtros.pop("nombre_completo", None)
    vendedores = await obtenerVendedor(filtros=filtros, columnas=columnas)
    if not vendedores:
        return vendedores
    # Vincula el vendedor con su usuario por id_usuariofk (tabla `vendedores`)
    # pero sin adjuntar `usuario.rol`
    vendedores = await attach_related(vendedores, 'id_usuariofk', obtener_usuarios_sin_rol, 'id', 'id', 'usuario')
    if nombre_completo:
        vendedores = filtrar_por_nombre_completo(vendedores, nombre_completo, path=['usuario', 'persona'])
    return vendedores


async def crear_vendedor(payload: dict):
    vendedor = build_vendedor_entity(payload)
    return await actualizarVendedor(vendedor)


async def actualizar_vendedor(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarVendedor(payload, id)
