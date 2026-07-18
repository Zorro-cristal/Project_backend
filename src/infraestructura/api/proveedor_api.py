from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.proveedor_request import (
    ProveedorRequest, ProveedorUpdateRequest)

from ..services.proveedor_service import (actualizar_proveedor,
                                          crear_proveedor, obtener_proveedores)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('proveedor', 'editar'))], summary="Actualizar proveedor", description="Actualiza un proveedor existente por su ID.")
async def actualizarProveedorApi(id: int, requestBody: ProveedorUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_proveedor(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('proveedor', 'editar'))], summary="Actualizar proveedor parcialmente", description="Actualiza parcialmente un proveedor existente por su ID.")
async def patchProveedorApi(id: int, requestBody: ProveedorUpdateRequest):
    return await actualizarProveedorApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('proveedor', 'crear'))], summary="Crear proveedor", description="Crea un nuevo proveedor.")
async def agregarProveedorApi(requestBody: ProveedorRequest):
    payload = requestBody.model_dump()
    result = await crear_proveedor(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('proveedor', 'leer'))], summary="Obtener proveedores", description="Obtiene una lista de proveedores con filtros opcionales.")
async def obtenerProveedoresApi(
    id: Optional[str] = Query(None, description="Filtrar proveedores por ID"),
    razon_social: Optional[str] = Query(None, description="Filtrar proveedores por razón social parcial"),
    ruc: Optional[int] = Query(None, description="Filtrar proveedores por RUC"),
    estado: Optional[int] = Query(None, description="Filtrar proveedores por estado (1 activo, 0 inactivo)"),
    correo: Optional[str] = Query(None, description="Filtrar proveedores por correo"),
    id_personafk: Optional[int] = Query(None, description="Filtrar proveedores por ID de persona asociada"),
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if razon_social is not None:
        filtros["razon_social"] = razon_social
    if ruc is not None:
        filtros["ruc"] = ruc
    if estado is not None:
        filtros["estado"] = estado
    if correo is not None:
        filtros["correo"] = correo
    if id_personafk is not None:
        filtros["id_personafk"] = id_personafk
    if mostrar_inactivo != 1 and "estado" not in filtros:
        filtros["mostrar_inactivo"] = 0  # estado != 0

    result = await obtener_proveedores(filtros)

    # Si se filtra por id, devolvemos un array con el único proveedor (misma forma que /proveedor con id).
    if id is not None:
        if not result:
            return {"message": f"Proveedor con ID {id} no encontrado"}
        return {"message": result if isinstance(result, list) else [result]}

    return {"message": result}
