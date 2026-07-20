from src.infraestructura.models.usuario import Usuario
from src.infraestructura.repositories.permiso_rol_repository import \
    obtenerPermisosPorRol
from src.infraestructura.repositories.usuario_repository import obtenerUsuarios
from src.infraestructura.services.rol_service import obtener_roles
from src.shared.security.password_hasher import verify_password
from src.shell.utils import attach_related


async def procesarLogin(usuario: Usuario):
    # Buscamos solo por alias (no por contraseña en texto plano).
    filtro = {
        'alias': usuario.alias,
    }
    result = await obtenerUsuarios(filtro, 1, 0)

    if not result:
        return []

    usuario_db = result[0]
    contra_db = usuario_db.get('contra')

    if not contra_db:
        return []

    if verify_password(usuario.contra, contra_db):
        # Enriquecer con el rol del usuario
        result = await attach_related(
            result,
            'id_rolfk',
            obtener_roles,
            'id',
            'id',
            'rol'
        )
        
        # Obtener los permisos del rol
        id_rol = usuario_db.get('id_rolfk')
        if id_rol:
            permisos = await obtenerPermisosPorRol(id_rol)
        # Agregar permisos al resultado
        result[0]['permisos'] = permisos

        # Sanitizar para no devolver la contraseña al cliente
        result[0].pop('contra', None)

        return result


    return []
