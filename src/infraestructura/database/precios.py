from src.shell.adaptadores.database.generic_crud import get, insert, update

async def obtenerPrecio(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('precios', filtros, limite, offset)

async def actualizarPrecio(datos, id= 0):
    campos_excluir= ['producto_id']

    # Prepara el payload
    payload = prepararPayloadDb(datos, exclude_fields=campos_excluir)

    if id is None:
        id_precio= await insert('precio', payload)

        # Se prepara los datos para agregar asociar al producto
        await actualizarDetallePrecio(datos)
        return id_precio
    return await update('precio', id, payload)