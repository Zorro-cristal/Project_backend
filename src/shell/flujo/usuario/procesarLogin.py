from src.infraestructura.repositories.usuario_repository import obtenerUsuarios
from src.infraestructura.models.usuario import Usuario

async def procesarLogin(usuario: Usuario):
    filtro= {
        'alias': usuario.alias,
        'contra': usuario.contra,
    }
    result= await obtenerUsuarios(filtro, 1, 0)
    return result