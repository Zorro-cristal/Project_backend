from src.infraestructura.database.usuario import obtenerUsuarios
from src.infraestructura.entidad.usuario import Usuario

async def procesarLogin(usuario: Usuario):
    filtro= {
        'alias': usuario.alias,
        'contra': usuario.contra,
    }
    result= await obtenerUsuarios(filtro, 1, 0)
    return result