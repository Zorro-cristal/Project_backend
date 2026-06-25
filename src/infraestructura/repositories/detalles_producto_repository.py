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
        # Construir filtros para producto si se proporcionan
        producto_select = "id,nombre,impuesto,pesable,costeo,unidad_medida,id_categoriafk,id_marcafk,descripcion,estado,perecedero,es_ingrediente,es_comida,categorias(id,nombre),marcas(id,nombre)"
        
        # Inicializar como lista vacía por defecto
        productos_data = []
        
        # Aplicar filtros a producto si existen
        if filtros_producto:
            q = filtros_producto.get("q")
            es_comida = filtros_producto.get("es_comida")
            
            # Si hay filtros, necesitamos hacer una consulta más compleja
            # Supabase no permite filtrar relaciones directamente, así que primero obtenemos los IDs de productos
            if q or es_comida is not None:
                filtros_prod = {}
                # Para búsqueda con "q", necesitamos usar ikw::ilike.%valor% en PostgREST
                # Pero como generic_crud no soporta ilike directamente, hacemos la query sin filtro de nombre primero
                # y luego filtramos en memoria si hay resultados
                if es_comida is not None:
                    filtros_prod["es_comida"] = es_comida
                
                # Obtener IDs de productos que coinciden con los filtros
                from src.shell.adapters.database.generic_crud import \
                    get as db_get
                productos_data = await db_get('productos', filtros_prod, limit=limite, offset=offset)
                
                # Filtrar por nombre en memoria si hay query de búsqueda
                if q and productos_data:
                    q_lower = q.lower()
                    productos_data = [p for p in productos_data if q_lower in (p.get('nombre') or '').lower()]
        
        # Siempre procesamos el resultado (ahora productos_data está definido)
        if productos_data:
            producto_ids = [p['id'] for p in productos_data]
            # Agregar filtro para detalles_producto
            if filtros is None:
                filtros = {}
            filtros["id_productofk"] = producto_ids
        # Si no hay productos que coincidan, continuamos sin filtro
        # Esto permitirá que la consulta retorne vacío naturalmente
        
        relaciones.append(f"id_productofk:productos({producto_select})")
    
    if include_precios:
        # Incluir precios directamente a través de detalles_precio
        # Usando la sintaxis de Supabase para traer el array de precios directamente
        relaciones.append("detalles_precio(id_preciofk(id,monto,valido_desde,valido_hasta))")
    
    # Construir columnas con relaciones
    if relaciones:
        columnas = f"*, {', '.join(relaciones)}"
    
    return await get('detalles_producto', filtros, limite, offset, columns=columnas)


async def actualizarDetalleProducto(datos: Union[detalles_producto, dict], cod_barra: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    # Asegurar que id_productofk venga siempre (BD lo exige como NOT NULL)
    if payload.get('id_productofk') is None:
        raise ValueError('id_productofk es requerido para insertar/actualizar detalles_producto')

    if cod_barra is None:
        return await insert('detalles_producto', payload)
    return await update('detalles_producto', cod_barra, payload, key='cod_barra')
