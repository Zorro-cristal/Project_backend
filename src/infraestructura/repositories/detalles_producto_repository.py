from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.detalles_producto import detalles_producto


async def obtenerDetalleProducto(
    filtros=None, 
    limite=100, 
    offset=0, 
    columnas="*", 
    include_producto: bool = False,
    include_precios: bool = False,
    filtros_producto: Optional[dict] = None
):
    # Si se solicita incluir producto, usamos la columna específica con la relación
    # pero excluyendo detalles_producto del producto para evitar ciclos
    relaciones = []
    
    if include_producto:
        producto_select = "id,nombre,impuesto,pesable,costeo,unidad_medida,id_categoriafk,id_marcafk,descripcion,estado,perecedero,es_ingrediente,es_comida,marcas(id,nombre)"
        relaciones.append(f"id_productofk:productos({producto_select})")
    
    if include_precios:
        # Incluir precios directamente a través de detalles_precio
        # Usando la sintaxis de Supabase para traer el array de precios directamente
        relaciones.append("detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))")
    
    # Construir columnas con relaciones
    if relaciones:
        columnas = f"*, {', '.join(relaciones)}"
    
    result = await get('detalles_producto', filtros, limite, offset, columns=columnas)
    
    # Aplicar filtros en memoria (q, es_comida) con semántica de unión
    if filtros_producto:
        q = filtros_producto.get("q")
        es_comida = filtros_producto.get("es_comida")
        
        if result and (q or es_comida is not None):
            filtered = []
            for item in result:
                # Determinar si el ítem coincide con q (búsqueda en cod_barra y/o nombre de producto)
                match_q = True
                if q:
                    q_lower = q.lower()
                    
                    # Buscar en cod_barra (siempre, como string para búsqueda por contenido)
                    cod_barra = item.get('cod_barra')
                    cod_barra_str = str(cod_barra) if cod_barra is not None else ''
                    match_cod_barra = q_lower in cod_barra_str.lower()
                    
                    # Buscar en nombre de producto (solo si include_producto)
                    match_nombre = False
                    if include_producto:
                        producto = item.get('id_productofk') or item.get('producto')
                        if isinstance(producto, dict):
                            nombre = producto.get('nombre') or ''
                            match_nombre = q_lower in nombre.lower()
                    
                    # Unión (OR): coincide si el q aparece en cod_barra o en el nombre del producto
                    match_q = match_cod_barra or match_nombre
                
                # Aplicar filtro es_comida en memoria sobre el producto unido (solo si include_producto)
                match_es_comida = True
                if es_comida is not None and include_producto:
                    producto = item.get('id_productofk') or item.get('producto')
                    if isinstance(producto, dict):
                        prod_es_comida = producto.get('es_comida')
                        match_es_comida = str(prod_es_comida).lower() == str(es_comida).lower()
                    else:
                        match_es_comida = False
                
                if match_q and match_es_comida:
                    filtered.append(item)
            result = filtered
    
    # Normalizar campos para mejor experiencia de API
    if result:
        for item in result:
            # Supabase devuelve la relación como 'id_productofk' cuando se incluye producto
            if include_producto and 'id_productofk' in item:
                item['producto'] = item.pop('id_productofk')

            # Renombrar el campo detalles_precio a precios
            if include_precios and 'detalles_precio' in item:
                item['precios'] = item.pop('detalles_precio')
    
    return result


async def actualizarDetalleProducto(datos: Union[detalles_producto, dict], cod_barra: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    # Asegurar que id_productofk venga siempre (BD lo exige como NOT NULL)
    if payload.get('id_productofk') is None:
        raise ValueError('id_productofk es requerido para insertar/actualizar detalles_producto')

    if cod_barra is None:
        return await insert('detalles_producto', payload)
    return await update('detalles_producto', cod_barra, payload, key='cod_barra')
