from typing import Annotated, Optional

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
    q: Annotated[Optional[str], Query(description="Buscar por nombre completo de la persona asociada (nombre, apellido o cedula, contiene)")] = None,
    id: Annotated[Optional[str], Query(description="Filtrar vendedores por ID")] = None,
    salario: Annotated[Optional[float], Query(description="Filtrar vendedores por salario mínimo")] = None,
    comision: Annotated[Optional[float], Query(description="Filtrar vendedores por comisión")] = None,
    estado: Annotated[Optional[int], Query(description="Filtrar vendedores por estado (1 activo, 0 inactivo)")] = None,
    id_usuariofk: Annotated[Optional[int], Query(description="Filtrar vendedores por ID de usuario asociado")] = None,
    mostrar_inactivo: Annotated[Optional[int], Query(description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos")] = None,
    limit: Annotated[int, Query(ge=0, description="Cantidad máxima de registros a devolver")] = 100,
    offset: Annotated[int, Query(ge=0, description="Offset desde el cual devolver registros, por defecto 0")] = 0,
):
    filtros = {}
    if q is not None:
        if q.isnumeric():
            filtros["__filtro_compuesto"] = (
                "personas.cedula LIKE ? OR vendedores.id LIKE ?",
                (f"%{q}%", f"%{q}%"),
            )
        else:
            q = q.replace(" ", "%")
            filtros["__filtro_compuesto"] = (
                "personas.nombres LIKE ? OR personas.apellidos LIKE ?",
                (f"%{q}%", f"%{q}%"),
            )
    if id is not None:
        filtros["id"] = id
    if salario is not None:
        filtros["salario"] = salario

    if estado is not None:
        filtros["estado"] = estado
    if id_usuariofk is not None:
        filtros["id_usuariofk"] = id_usuariofk
    if mostrar_inactivo != 1 and "estado" not in filtros:
        filtros["mostrar_inactivo"] = 0  # estado != 0

    result = await obtener_vendedores(filtros=filtros, columnas='*', limite=limit, offset=offset)

    # Si se filtra por id, se busca un vendedor específico.
    # Se mantiene el "contrato" del endpoint: devolver un array (con un solo vendedor).
    if id is not None:
        if not result:
            return {"message": f"Vendedor con ID {id} no encontrado"}
        return {"message": result if isinstance(result, list) else [result]}

    return {"message": result}

