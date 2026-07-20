from src.shared.security.password_hasher import hash_password
from src.shell.utils import attach_related

from ..models.usuario import Usuario
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


async def obtener_usuarios(filtros: dict = None, columnas: str = '*'):
    usuarios = await obtenerUsuarios(filtros, 100, 0)
    if not usuarios:
        return usuarios

    usuarios = await attach_related(usuarios, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'persona')
    usuarios = await attach_related(usuarios, 'id_rolfk', obtener_roles, 'id', 'id', 'rol')

    # Sanitizar para no exponer la contraseña
    for u in usuarios:
        u.pop('contra', None)

    return usuarios


async def obtener_usuarios_sin_rol(filtros: dict = None, columnas: str = '*'):
    """
    Igual que `obtener_usuarios` pero NO adjunta el rol completo.
    Útil para endpoints GET donde se incluye `usuario` anidado
    pero no se quiere exponer `usuario.rol`.
    """
    usuarios = await obtenerUsuarios(filtros, 100, 0)
    if not usuarios:
        return usuarios

    usuarios = await attach_related(usuarios, 'id_personafk', obtener_personas, 'cedula', 'cedula', 'persona')

    # Sanitizar para no exponer la contraseña (cubre /vendedor que adjunta usuario)
    for u in usuarios:
        u.pop('contra', None)

    return usuarios



async def crear_usuario(payload: dict):
    # Extraer y procesar la persona relacionada
    id_persona = None
    
    # Prioridad 1: Si ya viene id_personafk directamente, usarlo
    if 'id_personafk' in payload and payload['id_personafk']:
        id_persona = payload.get('id_personafk')
    elif 'persona' in payload and payload['persona']:
        # Prioridad 2: Si viene objeto persona, procesarlo
        persona_data = payload.pop('persona')  # Extraer y remover del payload principal
        cedula = persona_data.get('cedula')
        
        if cedula:
            # Verificar si la persona ya existe
            personas_existentes = await obtener_personas({'cedula': cedula})
            
            if personas_existentes:
                # La persona existe, actualizamos sus datos
                await actualizar_persona(cedula, persona_data)
                id_persona = cedula  # La cedula es la clave primaria en Persona
            else:
                # Crear nueva persona
                nueva_persona = await crear_persona(persona_data)
                id_persona = persona_data.get('cedula')
    
    # Agregar el id_personafk al payload si existe
    if id_persona is not None:
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
