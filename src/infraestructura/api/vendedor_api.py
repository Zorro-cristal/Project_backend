from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.vendedor_request import (
    VendedorRequest, VendedorUpdateRequest)

from ..services.vendedor_service import (actualizar_vendedor, crear_vendedor,
                                         obtener_vendedores)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('vendedor', 'editar'))], summary="Actualizar vendedor", description="Actualiza un vendedor existente por su ID.")
async def actualizarVendedorApi(id: int, requestBody: VendedorUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_vendedor(id, payload)
    return {"message": result}

@router.patch("/{id}", dependencies=[Depends(permiso_requerido('vendedor', 'editar'))], summary="Actualizar vendedor parcialmente", description="Actualiza parcialmente un vendedor existente por su ID.")
async def patchVendedorApi(id: int, requestBody: VendedorUpdateRequest):
    return await actualizarVendedorApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('vendedor', 'crear'))], summary="Crear vendedor", description="Crea un nuevo vendedor.")
async def agregarVendedorApi(requestBody: VendedorRequest):
    payload = requestBody.model_dump()
    result = await crear_vendedor(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('vendedor', 'leer'))], summary="Obtener vendedores", description="Obtiene una lista de vendedores con filtros opcionales.")
async def obtenerVendedoresApi(
    id: Optional[str] = Query(None, description="Filtrar vendedores por ID"),
    salario: Optional[float] = Query(None, description="Filtrar vendedores por salario mínimo"),
    comision: Optional[float] = Query(None, description="Filtrar vendedores por comisión"),
    estado: Optional[int] = Query(None, description="Filtrar vendedores por estado (1 activo, 0 inactivo)"),
    id_usuariofk: Optional[int] = Query(None, description="Filtrar vendedores por ID de usuario asociado"),
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if salario is not None:
        filtros["salario"] = salario
    if comision is not None:
        filtros["comision"] = comision
    if estado is not None:
        filtros["estado"] = estado
    if id_usuariofk is not None:
        filtros["id_usuariofk"] = id_usuariofk
    if mostrar_inactivo != 1 and "estado" not in filtros:
        filtros["mostrar_inactivo"] = 0  # estado != 0

    result = await obtener_vendedores(filtros)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('vendedor', 'leer'))], summary="Obtener vendedor por ID", description="Obtiene un vendedor específico por su ID.")
async def obtenerVendedorPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_vendedores(filtros)
    if not result:
        return {"message": f"Vendedor con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
