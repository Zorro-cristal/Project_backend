from src.shell.utils import filtrar_por_nombre_completo

from ..models.persona import Persona
from ..repositories.persona_repository import actualizarPersona, obtenerPersona


def build_persona_entity(payload: dict) -> Persona:
    valid_fields = {key: value for key, value in payload.items() if key in Persona.__annotations__}
    return Persona(**valid_fields)


async def obtener_personas(filtros: dict= None, columnas: str = '*'):
    filtros = dict(filtros or {})
    nombre_completo = filtros.pop("nombre_completo", None)
    result = await obtenerPersona(filtros=filtros, columnas=columnas)
    if nombre_completo:
        result = filtrar_por_nombre_completo(result, nombre_completo)
    return result


async def crear_persona(payload: dict):
    persona = build_persona_entity(payload)
    return await actualizarPersona(persona)


async def actualizar_persona(cedula: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPersona(payload, cedula)
