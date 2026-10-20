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
    joins = []
    
    # Definir columnas base para el producto
    producto_cols = "id,nombre,impuesto,pesable,costeo,unidad_medida,id_categoriafk,id_marcafk,descripcion,estado,perecedero,es_ingrediente,es_comida"

    if include_producto:
        joins.append({
            "table": "productos",
            "foreign_key": "id_productofk",
            "primary_key": "id",
            "type": "LEFT",
        })

    if include_precios:
        joins.append({
            "table": "detalles_precio",
            "foreign_key": "id_detalles_productofk",
            "primary_key": "id",
            "type": "LEFT",
        })

    filtros = dict(filtros or {})
    stock_minimo = filtros.pop("stock_minimo", None)
    if stock_minimo is not None:
        filtros["stock_total_inicio"] = stock_minimo
    
    # Construir columnas con relaciones usando proyecciones anidadas para evitar aplanamiento y colisiones
    if include_producto and include_precios:
        columnas = f"*, productos({producto_cols}), detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))"
    elif include_producto:
        columnas = f"*, productos({producto_cols})"
    elif include_precios:
        columnas = f"* , detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))"

    result = await get(
        'detalles_producto_con_stock', 
        filtros, 
        limite, 
        offset, 
        columns=columnas,
        joins=joins if joins else None
    )
    
    # Aplicar filtros en memoria (q, es_comida) con semántica de unión
    if filtros_producto:
        q = filtros_producto.get("q")
        es_comida = filtros_producto.get("es_comida")
        
        if result and (q or es_comida is not None):
            filtered = []
            for item in result:
                match_q = True
                if q:
                    q_lower = q.lower()
                    cod_barra = str(item.get('cod_barra') or '')
                    match_cod_barra = q_lower in cod_barra.lower()
                    
                    match_nombre = False
                    if include_producto:
                        # El objeto producto puede venir en la llave 'productos' por la proyección anidada
                        producto = item.get('productos') or item.get('producto')
                        if isinstance(producto, dict):
                            nombre = producto.get('nombre') or ''
                            match_nombre = q_lower in nombre.lower()
                    
                    match_q = match_cod_barra or match_nombre
                
                match_es_comida = True
                if es_comida is not None and include_producto:
                    producto = item.get('productos') or item.get('producto')
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
            # Asegurar que el campo 'producto' sea un diccionario si se solicitó y existe la relación
            if include_producto:
                if 'productos' in item and isinstance(item['productos'], dict):
                    item['producto'] = item.pop('productos')

            # Renombrar y aplanar el campo detalles_precio a precios
            if include_precios and 'detalles_precio' in item:
                raw_precios = item.pop('detalles_precio')
                item['precios'] = [p.get('id_preciofk') if isinstance(p, dict) and 'id_preciofk' in p else p for p in raw_precios]
    
    return result



async def actualizarDetalleProducto(datos: Union[detalles_producto, dict], cod_barra: Optional[str] = None):
    payload = prepararPayloadDb(datos)

    # Asegurar que id_productofk venga siempre (BD lo exige como NOT NULL)
    if payload.get('id_productofk') is None:
        raise ValueError('id_productofk es requerido para insertar/actualizar detalles_producto')

    if cod_barra is None:
        return await insert('detalles_producto', payload)
    return await update('detalles_producto', cod_barra, payload, key='cod_barra')
