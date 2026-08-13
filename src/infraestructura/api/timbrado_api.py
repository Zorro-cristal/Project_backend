from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.timbrado_request import (EmitirCodNumRequest,
                                                          TimbradoBase,
                                                          TimbradoUpdate)

from ..services.timbrado_service import (actualizar_timbrado, crear_timbrado,
                                         emitir_cod_num_venta,
                                         obtener_secuencias_venta,
                                         obtener_timbrado_por_id,
                                         obtener_timbrados)

router = APIRouter()




@router.get("/", dependencies=[Depends(permiso_requerido("timbrado", "leer"))])
async def listar_timbrados(
    id: Optional[int] = None,
    fin_vigencia_inicio: Optional[str] = None,
    fin_vigencia_fin: Optional[str] = None,
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    try:
        filtros = {}
        if id is not None:
            filtros["id"] = id
        if fin_vigencia_inicio is not None:
            filtros["fin_vigencia_inicio"] = fin_vigencia_inicio
        if fin_vigencia_fin is not None:
            filtros["fin_vigencia_fin"] = fin_vigencia_fin

        return {"message": await obtener_timbrados(filtros=filtros, limite=limit, offset=offset)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{id}", dependencies=[Depends(permiso_requerido("timbrado", "leer"))])
async def obtener_timbrado(id: int):
    try:
        timbrado = await obtener_timbrado_por_id(id)
        if not timbrado:
            return {"message": None}
        return {"message": timbrado}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/",
    dependencies=[Depends(permiso_requerido("timbrado", "crear"))],
    summary="Crear timbrado",
)
async def crear_timbrado_api(body: TimbradoBase):
    try:
        payload = body.model_dump()
        return {"message": await crear_timbrado(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put(
    "/{id}",
    dependencies=[Depends(permiso_requerido("timbrado", "editar"))],
    summary="Actualizar timbrado",
)
async def actualizar_timbrado_api(id: int, body: TimbradoUpdate):
    try:
        payload = body.model_dump(exclude_unset=True)
        if not payload:
            raise HTTPException(status_code=400, detail="Sin campos para actualizar")
        return {"message": await actualizar_timbrado(id, payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/secuencias-venta",
    dependencies=[Depends(permiso_requerido("timbrado", "leer"))],
    summary="Listar secuencias_venta",
)
async def listar_secuencias_venta(
    id_localfk: Optional[int] = None,
    id_vendedorfk: Optional[int] = None,
    id_timbradofk: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
):
    try:
        filtros = {}
        if id_localfk is not None:
            filtros["id_localfk"] = id_localfk
        if id_vendedorfk is not None:
            filtros["id_vendedorfk"] = id_vendedorfk
        if id_timbradofk is not None:
            filtros["id_timbradofk"] = id_timbradofk

        return {
            "message": await obtener_secuencias_venta(filtros=filtros, limite=limit, offset=offset)
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/emitir-cod-num-venta",
    dependencies=[Depends(permiso_requerido("timbrado", "crear"))],
    summary="Emitir cod_num de venta (sin RPC/SQL)",
    description="Genera cod_num_completo y actualiza secuencias_venta. Nota: no es atómico ante concurrencia sin lock/SQL.",
)
async def emitir_cod_num_venta_api(body: EmitirCodNumRequest):
    try:
        result = await emitir_cod_num_venta(id_local=body.id_local, id_vendedor=body.id_vendedor)
        return {"message": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
