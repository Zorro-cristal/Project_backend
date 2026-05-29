from src.infraestructura.models.usuario import Usuario
from src.infraestructura.repositories.usuario_repository import obtenerUsuarios
from src.shared.security.password_hasher import verify_password


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
        return result

    return []
