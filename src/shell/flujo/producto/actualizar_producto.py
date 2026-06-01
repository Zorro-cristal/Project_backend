from src.infraestructura.repositories.precio_repository import (
    actualizarPrecio, crearPrecio, vincular_precio_detalle)

async def actualizarDetallesDesdeProducto(detalles):
    for detalle in detalles:
        # obtener código de barra del detalle
        cod_barra = detalle.get('cod_barra') if isinstance(detalle, dict) else getattr(detalle, 'cod_barra', None)
        precios = detalle.get('precios') if isinstance(detalle, dict) else getattr(detalle, 'precios', None)
        if not precios:
            continue
        for precio in precios:
            # Si el precio tiene id => actualizar, sino crear y vincular
            precio_id = precio.get('id') if isinstance(precio, dict) else getattr(precio, 'id', None)
            if precio_id:
                await actualizarPrecio(precio, precio_id)
            else:
                creado = await crearPrecio(precio)
                nuevo_id = creado.get('id')
                if nuevo_id:
                    await vincular_precio_detalle(nuevo_id, cod_barra)