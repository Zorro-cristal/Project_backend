
async def obtenerDetallePrecio(filtros= None, limite= 100, offset= 0, columnas= "*"):
    return await get('detalles_precio', filtros, limite, offset)

async def actualizarDetallePrecio(datos, id= 0):
    payload = prepararPayloadDb(datos)
    
    if id is None:
        await insert('detalles_precio', payload)
    return await update('precio', id, payload)