from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb


async def obtenerUsuarios(filtros, limite, offset, columnas= '*'):
    joins = [{
        "table": "personas",
        "foreign_key": "id_personafk",
        "primary_key": "cedula",
        "type": "LEFT",
    }]
    return await get(
        'usuarios',
        filtros,
        limite,
        offset,
        columns=columnas + ", personas(nombres, apellidos, telefono)",
        joins=joins,
    )

async def actualizarUsuario(datos, id= 0):
    # Excluimos explícitamente los objetos complejos y campos que no pertenecen a la tabla usuarios
    payload = prepararPayloadDb(datos, exclude_fields=['personas', 'rol', 'persona'])
    if id == 0:
        return await insert('usuarios', payload)
    return await update('usuarios', id, payload)