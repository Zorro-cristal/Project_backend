from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.compra_request import (CompraRequest,
                                                        CompraUpdateRequest)
from src.shell.flujo.compra.consultarCompra import obtener_compra_con_detalles

from ..services.compra_service import (actualizar_compra,
                                       crear_compra_a_credito,
                                       crear_compra_con_pago, obtener_compras)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('compra', 'editar'))], summary="Actualizar compra", description="Actualiza una compra existente por su ID.")
async def actualizarCompraApi(id: int, requestBody: CompraUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_compra(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('compra', 'editar'))], summary="Actualizar compra parcialmente", description="Actualiza parcialmente una compra existente por su ID.")
async def patchCompraApi(id: int, requestBody: CompraUpdateRequest):
    return await actualizarCompraApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('compra', 'crear'))], summary="Crear compra", description="Crea una nueva compra.")
async def agregarCompraApi(requestBody: CompraRequest):
    payload = requestBody.model_dump()
    try:
        # tipo_credito obligatorio: 0=contado, 1=crédito
        tipo_credito = payload.get('tipo_credito')
        if tipo_credito is None:
            raise ValueError('Para crear una compra se requiere tipo_credito')
        if tipo_credito == 1:
            result = await crear_compra_a_credito(payload)
        else:
            result = await crear_compra_con_pago(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('compra', 'leer'))], summary="Obtener compras", description="Obtiene una lista de compras con filtros opcionales.")
async def obtenerComprasApi(
    id: Optional[int] = Query(None, description="Filtrar compras por ID"),
    nro: Optional[str] = Query(None, description="Filtrar compras por número"),
    id_localfk: Optional[int] = Query(None, description="Filtrar compras por ID de local"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar compras por ID de cliente"),
    id_proveedorfk: Optional[int] = Query(None, description="Filtrar compras por ID de proveedor"),
    estado: Optional[int] = Query(None, description="Filtrar compras por estado"),
    nombre_usuario: Optional[str] = Query(None, description="Filtrar compras por nombre de usuario (alias del usuario que creó la caja)"),
    include: Optional[str] = Query(None, description="Incluye datos adicionales. Soporta: detallesCompra"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    from src.infraestructura.config.supabase import get_supabase_client
    
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nro is not None:
        filtros["nro"] = nro
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk
    if id_clientefk is not None:
        filtros["id_clientefk"] = id_clientefk
    if id_proveedorfk is not None:
        filtros["id_proveedorfk"] = id_proveedorfk
    if estado is not None:
        filtros["estado"] = estado

    # Si se provee nombre_usuario, filtrar en dos pasos:
    # 1. Buscar usuarios con ese alias
    # 2. Buscar cajas creadas por esos usuarios
    # 3. Filtrar compras por esas cajas
    if nombre_usuario:
        client = get_supabase_client()
        
        # Paso 1: Buscar usuario(s) por alias
        usuarios = client.table('usuarios').select('id').eq('alias', nombre_usuario).execute()
        
        if usuarios.data:
            usuario_ids = [u['id'] for u in usuarios.data]
            
            # Paso 2: Buscar cajas creadas por esos usuarios
            cajas = client.table('cajas').select('id').in_('id_usuariofk', usuario_ids).execute()
            
            if cajas.data:
                caja_ids = [c['id'] for c in cajas.data]
                filtros['id_cajafk'] = caja_ids
            else:
                # No hay cajas para esos usuarios, retornar vacío
                return {"message": []}

    result = await obtener_compras(filtros=filtros, joins=None, limite=limit, offset=offset)
    
    # Adjuntar detalles si se solicita
    if include == "detallesCompra":
        from src.shell.flujo.compra.consultarCompra import attach_related_data
        result = await attach_related_data(result) if result else result
    
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('compra', 'leer'))], summary="Obtener compra por ID", description="Obtiene una compra específica por su ID, incluyendo sus detalles.")
async def obtenerCompraPorIdApi(id: int):
    # Ya incluye detalles por defecto
    result = await obtener_compra_con_detalles(id)

    if not result:
        return {"message": f"Compra con ID {id} no encontrada"}
    return {"message": result}


@router.get("/{id}/detalleCompra", dependencies=[Depends(permiso_requerido('compra', 'leer'))], summary="Obtener detalles de compra", description="Obtiene solo los detalle_compra asociados a una compra.")
async def obtenerDetalleCompraPorIdApi(id: int):
    result = await obtener_compra_con_detalles(id, solo_detalles=True)
    return {"message": result}


