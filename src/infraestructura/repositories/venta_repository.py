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

    # 1) Primero obtenemos ventas desde la tabla física `ventas` con los filtros que apliquen.
    #    Nota: `id_localfk`/`id_vendedorfk` se manejan después.
    ventas_filtros = dict(filtros)
    ventas_filtros.pop("id_localfk", None)
    ventas_filtros.pop("id_vendedorfk", None)

    # Soporte para compatibilidad con filtros antiguos:
    # - algunos llaman con `fecha` como inicio
    if "fecha_inicio" not in ventas_filtros and "fecha" in ventas_filtros:
        ventas_filtros["fecha_inicio"] = ventas_filtros.pop("fecha")

    ventas = await get("ventas", ventas_filtros, limite, offset, columns=columnas, joins=joins)
    if not ventas:
        return []

    # 2) Si no se pidieron filtros por local/vendedor, devolvemos tal cual.
    if "id_localfk" not in filtros and "id_vendedorfk" not in filtros:
        return ventas

    # 3) Consultar secuencias_venta para obtener id_localfk e id_vendedorfk "virtuales".
    #    Necesitamos mapear por `id` (secuencias_venta.id) que está en ventas.id_secuencias_ventafk.
    id_seq_list = []
    for v in ventas:
        seq_id = v.get("id_secuencias_ventafk")
        if seq_id is not None:
            id_seq_list.append(seq_id)

    if not id_seq_list:
        return []

    # El generic_crud `get` soporta filtros simples; para IN usamos `in_`
    # así que consultamos en bruto vía RPC no, sino usando get con filtro.
    secuencias = await get(
        "secuencias_venta",
        {"id": id_seq_list},
        limite=len(id_seq_list),
        offset=0,
        columns="id,id_localfk,id_vendedorfk",
    )

    seq_map = {}
    for s in secuencias or []:
        sid = s.get("id")
        seq_map[sid] = s

    # 4) Adjuntar id_localfk/id_vendedorfk y filtrar en servidor.
    id_localfk_wanted = filtros.get("id_localfk")
    id_vendedorfk_wanted = filtros.get("id_vendedorfk")

    resultados = []
    for v in ventas:
        seq_id = v.get("id_secuencias_ventafk")
        s = seq_map.get(seq_id, {})
        v_out = dict(v)
        v_out["id_localfk"] = s.get("id_localfk")
        v_out["id_vendedorfk"] = s.get("id_vendedorfk")

        if id_localfk_wanted is not None and v_out["id_localfk"] != id_localfk_wanted:
            continue
        if id_vendedorfk_wanted is not None and v_out["id_vendedorfk"] != id_vendedorfk_wanted:
            continue

        resultados.append(v_out)

    return resultados


async def actualizarVenta(datos: Union[Venta, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['usuario', 'cliente', 'local', 'caja', 'detalles'])

    # Evitar persistir ids que ya no existen en la tabla `ventas`
    payload.pop("id_localfk", None)
    payload.pop("id_vendedorfk", None)

    if id is None:
        return await insert("ventas", payload)
    return await update("ventas", id, payload, key='id_venta')
