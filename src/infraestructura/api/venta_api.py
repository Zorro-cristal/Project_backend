from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query


from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.venta_request import (
    VentaBase,
    VentaUpdateRequest,
)

from ..services.venta_service import (
    actualizar_venta,
    crear_venta,
    obtener_detalle_venta_por_venta_id,
    obtener_venta_por_id_con_detalles,
    obtener_venta_por_id_sin_detalles,
    obtener_ventas,
)
from ..services.vendedor_service import obtener_vendedores

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('venta', 'editar'))], summary="Actualizar venta", description="Actualiza una venta existente por su ID.")
async def actualizarVentaApi(id: int, requestBody: VentaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_venta(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('venta', 'editar'))], summary="Actualizar venta parcialmente", description="Actualiza parcialmente una venta existente por su ID.")
async def patchVentaApi(id: int, requestBody: VentaUpdateRequest):
    return await actualizarVentaApi(id, requestBody)


@router.post(
    "/",
    dependencies=[Depends(permiso_requerido("venta", "crear"))],
    summary="Crear venta",
    description="Crea una nueva venta.",
)
async def agregarVentaApi(
    requestBody: VentaBase,
    current_user: dict = Depends(permiso_requerido("venta", "crear")),
):
    payload = requestBody.model_dump()

    # Compatibilidad:
    # - el modelo Venta guarda id_vendedorfk
    # - antes se enviaba id_usuariofk
    # Si llega id_vendedorfk, úsalo. Si llega id_usuariofk y no id_vendedorfk, resolver vendedor.
    if payload.get("id_vendedorfk") is None:
        id_usuariofk = payload.get("id_usuariofk")

        # Si no viene desde payload, tomar del usuario autenticado
        if id_usuariofk is None:
            id_usuariofk = (
                current_user.get("id")
                or current_user.get("id_usuariofk")
                or current_user.get("cedula")
            )

        if id_usuariofk is None:
            raise HTTPException(
                status_code=401,
                detail="No se pudo determinar el usuario autenticado (id_usuariofk).",
            )

        # Resolver vendedor por id_usuariofk
        vendedores = await obtener_vendedores({"id_usuariofk": id_usuariofk})
        if not vendedores:
            raise HTTPException(
                status_code=404,
                detail=f"No existe vendedor para el usuario autenticado (id_usuariofk={id_usuariofk}).",
            )

        vendedor = vendedores[0] if isinstance(vendedores, list) else vendedores
        payload["id_vendedorfk"] = vendedor.get("id")

    # Limpiar campos que no se deben persistir al crear
    # - id: la PK es identity en BD; si el cliente envía id (ej: 0/1), puede romper el INSERT.
    # - id_usuariofk: se deriva desde id_vendedorfk.
    payload.pop("id", None)
    payload.pop("id_usuariofk", None)
    # Evitar que viaje id interno del detalle_venta que podría usarse como PK en detalle_venta
    for d in payload.get("detalles_venta", []) or []:
        d.pop("id", None)


    try:
        result = await crear_venta(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Obtener ventas", description="Obtiene una lista de ventas con filtros opcionales.")
async def obtenerVentasApi(
    id: Optional[str] = Query(None, description="Filtrar ventas por ID"),
    fecha: Optional[str] = Query(None, description="Filtrar ventas por fecha"),
    estado: Optional[int] = Query(None, description="Filtrar ventas por estado"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar ventas por ID de cliente"),
    id_localfk: Optional[int] = Query(None, description="Filtrar ventas por ID de local"),
    id_cajafk: Optional[int] = Query(None, description="Filtrar ventas por ID de caja"),
    nombre_usuario: Optional[str] = Query(None, description="Filtrar ventas por nombre de usuario (alias del usuario que creó la caja)"),
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos")
):
    from src.infraestructura.config.supabase import get_supabase_client
    
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if fecha is not None:
        filtros["fecha"] = fecha
    if estado is not None:
        filtros["estado"] = estado
    if id_clientefk is not None:
        filtros["id_clientefk"] = id_clientefk
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk
    if id_cajafk is not None:
        filtros["id_cajafk"] = id_cajafk
    # Por defecto ocultar inactivos (estado=0), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = 1

    # Si se provee nombre_usuario, filtrar en dos pasos:datos:
    # (demo/example JSON mantenido como comentario; evita usar `false` que rompe Python)
    # {"id":0,"nro":"1","id_localfk":1,"id_clientefk":1,"id_mesafk":1,"fecha":"2026-07-06","estado":1,"tipo_credito":false,"detalles_venta":[{"id":0,"cantidad":1,"precio":55000,"descuento":0,"id_detalleproductofk":"2000000001","id_ordenfk":6}]}

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
    
    result = await obtener_ventas(filtros)

    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Obtener venta por ID", description="Obtiene una venta específica por su ID. Usa include=detalleVenta para incluir detalles.")
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



@router.get("/{id}/detalleVenta", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Obtener detalles de venta", description="Obtiene solo el detalle_venta asociado a una venta.")
async def obtenerDetalleVentaPorVentaIdApi(id: int):
    filtros = {"id_ventafk": id}
    result = await obtener_detalle_venta_por_venta_id(filtros)
    return {"message": result if result else []}


# Endpoints específicos para ventas con crédito (ahora redundantes - usar POST / con tipo_credito)

@router.post("/contado", dependencies=[Depends(permiso_requerido('venta', 'crear'))], summary="Crear venta al contado", description="Crea una venta al contado y registra el pago automáticamente.")
async def crearVentaContadoApi(requestBody: VentaBase):
    """Crea una venta al contado (tipo_credito=0) y registra el pago en pagos_venta."""
    payload = requestBody.model_dump()
    payload['tipo_credito'] = 0
    try:
        result = await crear_venta(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.post("/credito", dependencies=[Depends(permiso_requerido('venta', 'crear'))], summary="Crear venta a crédito", description="Crea una venta a crédito y genera las cuotas automáticamente.")
async def crearVentaCreditoApi(requestBody: VentaBase):
    """Crea una venta a crédito (tipo_credito=1) y genera las cuotas."""
    payload = requestBody.model_dump()
    payload['tipo_credito'] = 1
    try:
        result = await crear_venta(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/{id}/calcular-saldo", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Calcular saldo de venta crédito", description="Calcula el saldo pendiente de una venta a crédito usando lógica FIFO.")
async def calcularSaldoVentaApi(id: int):
    """Calcula el saldo restante de una venta a crédito aplicando lógica FIFO."""
    from ..services.cuota_venta_service import calcular_saldo_fifo
    try:
        result = await calcular_saldo_fifo(id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}



# ==========================
# Predicción de ventas (migrado a /venta)
# ==========================

from pydantic import BaseModel, Field

from src.infraestructura.services.prediccion_ventas_service import (
    build_daily_prediction_payloads,
    train_and_save_sales_forecast_model,
)


class TrainingRequest(BaseModel):
    limite: int | None = Field(None, description="Cantidad máxima de días de historial a usar")


@router.get(
    "/modelo/entrenar",
    summary="Entrenar modelo de predicción de ventas",
    description="Lee el historial de ventas desde Supabase, entrena un modelo local y lo guarda en disco.",
)
async def entrenar_modelo_ventas(
    limite: int | None = Query(None, description="Cantidad máxima de días de historial a usar"),
) -> dict[str, Any]:
    try:
        result = train_and_save_sales_forecast_model(limite=limite)
        return {"success": True, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al entrenar el modelo: {exc}") from exc


@router.get(
    "/modelo/predecir",
    summary="Predecir ventas proyectadas",
    description="Recibe un rango de fechas por query params, consulta clima real por día y devuelve la previsión diaria con ventas, recaudo y productos estimados.",
)
async def predecir_ventas(
    fecha_inicio: str = Query(..., description="Fecha inicial en formato YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha final en formato YYYY-MM-DD"),
    dias_festivos: list[str] | None = Query(None, description="Fechas festivas opcionales en formato YYYY-MM-DD"),
) -> dict[str, Any]:
    try:
        return build_daily_prediction_payloads(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias_festivos=dias_festivos or [],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al predecir: {exc}") from exc




