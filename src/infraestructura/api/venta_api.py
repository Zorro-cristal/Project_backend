from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.venta_service import (
    obtener_detalle_venta_por_venta_id, obtener_venta_por_id_con_detalles,
    obtener_venta_por_id_sin_detalles)
from src.shell.adapters.requests.venta_request import (VentaRequest,
                                                       VentaUpdateRequest)
from src.shell.flujo.venta.crearActualizarVenta import (
    actualizar_venta_por_id, crear_o_actualizar_venta)

router = APIRouter()


@router.put("/{id}", summary="Actualizar venta", description="Actualiza una venta existente por su ID.")
async def actualizarVentaApi(id: int, requestBody: VentaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_venta_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar venta parcialmente", description="Actualiza parcialmente una venta existente por su ID.")
async def patchVentaApi(id: int, requestBody: VentaUpdateRequest):
    return await actualizarVentaApi(id, requestBody)


@router.post("/", summary="Crear venta", description="Crea una nueva venta.")
async def agregarVentaApi(requestBody: VentaRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_venta(payload)
    return {"message": result}


@router.get("/", summary="Obtener ventas", description="Obtiene una lista de ventas con filtros opcionales.")
async def obtenerVentasApi(
    id: Optional[str] = Query(None, description="Filtrar ventas por ID"),
    nro: Optional[str] = Query(None, description="Filtrar ventas por número"),
    fecha: Optional[str] = Query(None, description="Filtrar ventas por fecha"),
    estado: Optional[int] = Query(None, description="Filtrar ventas por estado"),
    id_usuarioFK: Optional[int] = Query(None, description="Filtrar ventas por ID de usuario"),
    id_clienteFK: Optional[int] = Query(None, description="Filtrar ventas por ID de cliente"),
    id_localFK: Optional[int] = Query(None, description="Filtrar ventas por ID de local")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nro is not None:
        filtros["nro"] = nro
    if fecha is not None:
        filtros["fecha"] = fecha
    if estado is not None:
        filtros["estado"] = estado
    if id_usuarioFK is not None:
        filtros["id_usuarioFK"] = id_usuarioFK
    if id_clienteFK is not None:
        filtros["id_clienteFK"] = id_clienteFK
    if id_localFK is not None:
        filtros["id_localFK"] = id_localFK

    result = await obtener_ventas(filtros)

    return {"message": result}


@router.get("/{id}", summary="Obtener venta por ID", description="Obtiene una venta específica por su ID. Usa include=detalleVenta para incluir detalles.")
async def obtenerVentaPorIdApi(
    id: int,
    include: Optional[str] = Query(None, description="include=detalleVenta para incluir detalle_venta")
):
    filtros = {"id": id}

    if include == "detalleVenta":
        venta = await obtener_venta_por_id_con_detalles(filtros)
    else:
        venta = await obtener_venta_por_id_sin_detalles(filtros)

    if not venta:
        return {"message": f"Venta con ID {id} no encontrada"}

    return {"message": venta}



@router.get("/{id}/detalleVenta", summary="Obtener detalles de venta", description="Obtiene solo el detalle_venta asociado a una venta.")
async def obtenerDetalleVentaPorVentaIdApi(id: int):
    filtros = {"id_ventaFK": id}
    result = await obtener_detalle_venta_por_venta_id(filtros)
    return {"message": result if result else []}



