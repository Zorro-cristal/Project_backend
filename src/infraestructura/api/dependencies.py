from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infraestructura.services.usuario_service import obtener_usuarios
from src.shared.security.auth_handler import decodificar_token

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    payload = decodificar_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    
    user_id = payload.get("sub")
    # Buscamos al usuario para asegurar que existe y traer sus permisos
    # Nota: Aquí podrías cachear esto para no ir a DB en cada request
    usuarios = await obtener_usuarios({"id": user_id})
    if not usuarios:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return usuarios[0]

def permiso_requerido(modulo: str, accion: str): # modulo: 'Usuarios', accion: 'leer'
    async def controlador_permisos(current_user: dict = Depends(get_current_user)):
        permisos = current_user.get('permisos', [])

        tiene_permiso = any(
            p.get('permisos', {}).get('nombre') == modulo and p.get(accion) is True 
            for p in permisos
        )

        """ if not tiene_permiso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso de '{accion}' para el módulo '{modulo}'"
            ) """
        return current_user
    return controlador_permisos