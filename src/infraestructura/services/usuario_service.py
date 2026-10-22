from src.shared.security.password_hasher import hash_password
from src.shell.utils import attach_related

from ..models.usuario import Usuario
from ..repositories.rol_repository import obtenerRol
from ..repositories.usuario_repository import (actualizarUsuario,
                                               obtenerUsuarios)
from .persona_service import (actualizar_persona, crear_persona,
                              obtener_personas)
from .rol_service import obtener_roles


def build_usuario_entity(payload: dict) -> Usuario:
    valid_fields = {key: value for key, value in payload.items() if key in Usuario.__annotations__}
    return Usuario(**valid_fields)




def _hash_if_needed(payload: dict) -> dict:
    """Hashea la contraseña si viene en el payload.

    - Si 'contra' no está, no toca.
    - Si 'contra' ya parece hash (empieza con $2b/$2a/$2y), no lo rehashea.
      (Esto ayuda en actualizaciones parciales donde el backend reenvía el valor.)
    """
    if not isinstance(payload, dict):
        return payload

    if 'contra' not in payload:
        return payload

    contra = payload.get('contra')
    if contra is None:
        return payload

    if isinstance(contra, str) and (contra.startswith('$2a$') or contra.startswith('$2b$') or contra.startswith('$2y$')):
        return payload

    payload = dict(payload)
    payload['contra'] = hash_password(contra)
    return payload



# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


# Reemplazado por helper genérico `attach_related` en `src/shell/utils.py`


async def obtener_usuarios(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    filtros = dict(filtros or {})
    usuarios = await obtenerUsuarios(filtros, limite, offset, columnas=columnas)

    usuarios = await attach_related(usuarios, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'personas')

    # Sanitizar para no exponer la contraseña
    for u in usuarios:
        u.pop('contra', None)

    return usuarios


async def obtener_usuarios_sin_rol(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    """
    Igual que `obtener_usuarios` pero NO adjunta el rol completo.
    Útil para endpoints GET donde se incluye `usuario` anidado
    pero no se quiere exponer `usuario.rol`.
    """
    filtros = dict(filtros or {})
    
    usuarios = await obtenerUsuarios(filtros, limite, offset)
    if not usuarios:
        return usuarios

    # Sanitizar para no exponer la contraseña (cubre /vendedor que adjunta usuario)
    for u in usuarios:
        u.pop('contra', None)

    return usuarios



async def crear_usuario(payload: dict):
    payload = dict(payload)
    persona_data = payload.pop('personas', None)
    id_persona = payload.get('id_personafk')
    id_rol = payload.get('id_rolfk')

    if id_rol is None:
        raise ValueError('Se requiere id_rolfk')
    if not await obtenerRol(filtros={'id': id_rol}):
        raise ValueError(f'El rol con id {id_rol} no existe')

    if persona_data:
        cedula = persona_data.get('cedula')
        if id_persona is not None and id_persona != cedula:
            raise ValueError('id_personafk debe coincidir con la cedula de la persona')
        if cedula is None:
            raise ValueError('La persona requiere una cedula')

        personas_existentes = await obtener_personas({'cedula': cedula})
        if personas_existentes:
            await actualizar_persona(cedula, persona_data)
        else:
            await crear_persona(persona_data)
        id_persona = cedula
    elif id_persona is not None:
        if not await obtener_personas({'cedula': id_persona}):
            raise ValueError(f'La persona con cedula {id_persona} no existe')
    else:
        raise ValueError('Se requiere una persona o id_personafk existente')

    payload['id_personafk'] = id_persona

    # Hashear la contraseña si es necesario
    payload = _hash_if_needed(payload)
    
    # Construir la entidad usuario
    usuario = build_usuario_entity(payload)
    return await actualizarUsuario(usuario)


async def actualizar_usuario(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    payload = _hash_if_needed(payload)
    return await actualizarUsuario(payload, id)
