from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.venta import Venta


async def obtenerVenta(filtros=None, limite=100, offset=0, columnas="*", joins=None):
    """
    Obtiene ventas.
    - Mantiene soporte de filtros virtuales (id_localfk / id_vendedorfk) sin depender de RPC en BD.
    - Calcula id_localfk e id_vendedorfk consultando secuencias_venta.
    """
    filtros = filtros or {}

    # Las columnas local/vendedor viven en secuencias_venta, no en ventas.
    ventas_filtros = dict(filtros)
    id_local = ventas_filtros.pop("id_localfk", None)
    id_vendedor = ventas_filtros.pop("id_vendedorfk", None)

    # Soporte para compatibilidad con filtros antiguos:
    # - algunos llaman con `fecha` como inicio
    if "fecha_inicio" not in ventas_filtros and "fecha" in ventas_filtros:
        ventas_filtros["fecha_inicio"] = ventas_filtros.pop("fecha")

    seq_filters = {}
    if id_local is not None:
        seq_filters["id_localfk"] = id_local
    if id_vendedor is not None:
        seq_filters["id_vendedorfk"] = id_vendedor

    secuencias = await get(
        "secuencias_venta",
        seq_filters,
        limit=10000,
        offset=0,
        columns="id,id_localfk,id_vendedorfk",
    ) if seq_filters else []

    if seq_filters:
        if not secuencias:
            return []
        ventas_filtros["id_secuencias_ventafk"] = [seq["id"] for seq in secuencias]

    ventas = await get("ventas", ventas_filtros, limite, offset, columns=columnas, joins=joins)
    if not ventas or not seq_filters:
        return ventas

    secuencias_por_id = {secuencia["id"]: secuencia for secuencia in secuencias}
    for venta in ventas:
        secuencia = secuencias_por_id.get(venta.get("id_secuencias_ventafk"), {})
        venta["id_localfk"] = secuencia.get("id_localfk")
        venta["id_vendedorfk"] = secuencia.get("id_vendedorfk")
    return ventas


async def actualizarVenta(datos: Union[Venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario', 'cliente', 'local', 'caja', 'detalles'])

    # Evitar persistir ids que ya no existen en la tabla `ventas`
    payload.pop("id_localfk", None)
    payload.pop("id_vendedorfk", None)

    if id is None:
        return await insert("ventas", payload)
    return await update("ventas", id, payload, key='id')
