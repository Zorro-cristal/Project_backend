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
    # Definir columnas base para el producto
    producto_cols = "id,nombre,impuesto,pesable,costeo,unidad_medida,id_categoriafk,id_marcafk,descripcion,estado,perecedero,es_ingrediente,es_comida"

    filtros = dict(filtros or {})
    stock_minimo = filtros.pop("stock_minimo", None)
    cargar_producto = include_producto or stock_minimo is not None
    
    # Construir columnas con relaciones usando proyecciones anidadas para evitar aplanamiento y colisiones
    if cargar_producto and include_precios:
        columnas = f"*, productos({producto_cols}), detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))"
    elif cargar_producto:
        columnas = f"*, productos({producto_cols})"
    elif include_precios:
        columnas = f"* , detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))"

    result = await get(
        'detalles_producto',
        filtros,
        None if stock_minimo is not None else limite,
        0 if stock_minimo is not None else offset,
        columns=columnas,
    )

    if result:
        codigos_barra = [
            item["cod_barra"] for item in result if item.get("cod_barra") is not None
        ]
        stock_total_por_codigo: dict[str, int] = {}
        for inicio in range(0, len(codigos_barra), 500):
            lote_codigos = codigos_barra[inicio : inicio + 500]
            stocks = await get(
                "stocks",
                {"id_detalleproductofk": lote_codigos},
                limit=None,
                columns="id_detalleproductofk,cant_deposito,cant_mostrador",
            )
            for stock in stocks:
                codigo = stock["id_detalleproductofk"]
                stock_total_por_codigo[codigo] = stock_total_por_codigo.get(codigo, 0) + (
                    (stock.get("cant_deposito") or 0) + (stock.get("cant_mostrador") or 0)
                )
        for item in result:
            item["stock_total"] = stock_total_por_codigo.get(item.get("cod_barra"), 0)

    if stock_minimo is not None:
        productos_comida = {
            producto.get("id")
            for item in result
            for producto in [item.get("productos") or item.get("producto")]
            if isinstance(producto, dict)
            and producto.get("id") is not None
            and str(producto.get("es_comida")).lower() in {"true", "1", "t", "si", "y"}
        }

        if productos_comida:
            ingredientes = await get(
                "ingredientes",
                {"id_producto_finalfk": list(productos_comida)},
                limit=None,
                columns="id_producto_finalfk,id_producto_ingredientefk,cantidad",
            )
            cantidades_por_comida: dict[int, dict[int, int]] = {}
            for ingrediente in ingredientes:
                id_comida = ingrediente.get("id_producto_finalfk")
                id_ingrediente = ingrediente.get("id_producto_ingredientefk")
                cantidad = int(ingrediente.get("cantidad") or 0)
                if (
                    id_comida in productos_comida
                    and id_ingrediente is not None
                    and cantidad > 0
                ):
                    ingredientes_comida = cantidades_por_comida.setdefault(id_comida, {})
                    ingredientes_comida[id_ingrediente] = (
                        ingredientes_comida.get(id_ingrediente, 0) + cantidad
                    )

            ids_ingredientes = {
                id_ingrediente
                for cantidades in cantidades_por_comida.values()
                for id_ingrediente in cantidades
            }
            cod_barra_por_ingrediente: dict[int, str] = {}
            ids_ingredientes_lista = list(ids_ingredientes)
            for inicio in range(0, len(ids_ingredientes_lista), 500):
                lote_ids = ids_ingredientes_lista[inicio : inicio + 500]
                detalles_ingredientes = await get(
                    "detalles_producto",
                    {"id_productofk": lote_ids},
                    limit=None,
                    columns="id_productofk,cod_barra",
                )
                for detalle_ingrediente in detalles_ingredientes:
                    id_ingrediente = detalle_ingrediente.get("id_productofk")
                    cod_barra = detalle_ingrediente.get("cod_barra")
                    if id_ingrediente is not None and cod_barra is not None:
                        cod_barra_por_ingrediente.setdefault(id_ingrediente, cod_barra)

            stock_ingredientes_por_codigo: dict[str, int] = {}
            codigos_ingredientes = list(set(cod_barra_por_ingrediente.values()))
            for inicio in range(0, len(codigos_ingredientes), 500):
                lote_codigos = codigos_ingredientes[inicio : inicio + 500]
                stocks_ingredientes = await get(
                    "stocks",
                    {"id_detalleproductofk": lote_codigos},
                    limit=None,
                    columns="id_detalleproductofk,cant_deposito,cant_mostrador",
                )
                for stock in stocks_ingredientes:
                    codigo = stock["id_detalleproductofk"]
                    stock_ingredientes_por_codigo[codigo] = (
                        stock_ingredientes_por_codigo.get(codigo, 0)
                        + (stock.get("cant_deposito") or 0)
                        + (stock.get("cant_mostrador") or 0)
                    )

            for item in result:
                producto = item.get("productos") or item.get("producto")
                if not isinstance(producto, dict) or producto.get("id") not in productos_comida:
                    continue

                cantidades = cantidades_por_comida.get(producto["id"], {})
                porciones_disponibles = [
                    stock_ingredientes_por_codigo.get(
                        cod_barra_por_ingrediente.get(id_ingrediente), 0
                    )
                    // cantidad_por_porcion
                    for id_ingrediente, cantidad_por_porcion in cantidades.items()
                ]
                item["stock_total"] = min(porciones_disponibles, default=0)

        result = [item for item in result if item["stock_total"] >= stock_minimo]
        result = result[offset : None if limite is None else offset + limite]
    
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
                if es_comida is not None:
                    # Try to get the product object from either 'productos' or 'producto' keys
                    producto_obj = item.get('productos') or item.get('producto')
                    
                    val_to_check = None
                    if isinstance(producto_obj, dict):
                        val_to_check = producto_obj.get('es_comida')
                    
                    if val_to_check is None:
                        val_to_check = item.get('es_comida')

                    if val_to_check is not None:
                        # Normalize both to boolean for comparison
                        def to_bool(v):
                            if isinstance(v, bool): return v
                            if isinstance(v, (int, float)): return bool(v)
                            if isinstance(v, str):
                                if v.lower() in ('true', '1', 't', 'y', 'si'): return True
                                if v.lower() in ('false', '0', 'f', 'n', 'no'): return False
                            return bool(v)

                        match_es_comida = to_bool(val_to_check) == to_bool(es_comida)
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
            elif stock_minimo is not None:
                item.pop("productos", None)
                item.pop("producto", None)

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
