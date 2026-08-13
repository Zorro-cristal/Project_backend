from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

from src.infraestructura.models.timbrado import Timbrado
from src.shell.adapters.database.generic_crud import get, insert, update


async def obtener_timbrados(filtros: dict | None = None, limite: int = 100, offset: int = 0):
    return await get("timbrados", filtros or {}, limit=limite, offset=offset, columns="*")


async def obtener_timbrado_por_id(id: int):
    filas = await get("timbrados", {"id": id}, limit=1, offset=0, columns="*")
    return filas[0] if filas else None


def _normalize_fin_vigencia(fin_vigencia: Any) -> datetime:
    if isinstance(fin_vigencia, datetime):
        return fin_vigencia
    return datetime.fromisoformat(str(fin_vigencia))


def build_timbrado_entity(payload: dict) -> Timbrado:
    if not isinstance(payload, dict):
        raise ValueError("payload debe ser un dict")

    valid_fields = {key: value for key, value in payload.items() if key in Timbrado.__annotations__}

    if "fin_vigencia" in valid_fields and valid_fields.get("fin_vigencia") is not None:
        valid_fields["fin_vigencia"] = _normalize_fin_vigencia(valid_fields["fin_vigencia"])

    # id es opcional
    if "id" not in valid_fields and payload.get("id") is not None:
        valid_fields["id"] = payload.get("id")

    return Timbrado(**valid_fields)


async def crear_timbrado(payload: dict) -> dict:
    # Validación básica (estado/fechas)
    if payload.get("fin_vigencia") is None:
        raise ValueError("fin_vigencia es requerido")
    if payload.get("nro_timbrado") is None:
        raise ValueError("nro_timbrado es requerido")

    timbrado = build_timbrado_entity(
        {
            **payload,
            "nro_timbrado": str(payload.get("nro_timbrado")),
            "fin_vigencia": payload.get("fin_vigencia"),
            "id": payload.get("id"),
        }
    )

    fin_vigencia_serializable = timbrado.fin_vigencia
    if isinstance(fin_vigencia_serializable, datetime):
        fin_vigencia_serializable = fin_vigencia_serializable.isoformat()

    normalized_payload = {
        "nro_timbrado": timbrado.nro_timbrado,
        "fin_vigencia": fin_vigencia_serializable,
    }
    if timbrado.id is not None:
        normalized_payload["id"] = timbrado.id

    return await insert("timbrados", normalized_payload)


async def actualizar_timbrado(id: int, payload: dict) -> dict:
    if not payload:
        raise ValueError("No hay campos para actualizar")

    timbrado = build_timbrado_entity({**payload, "id": id})

    normalized_payload = {}
    if "nro_timbrado" in payload and payload.get("nro_timbrado") is not None:
        normalized_payload["nro_timbrado"] = str(timbrado.nro_timbrado)
    if "fin_vigencia" in payload and payload.get("fin_vigencia") is not None:
        fin_vigencia_serializable = timbrado.fin_vigencia
        if isinstance(fin_vigencia_serializable, datetime):
            fin_vigencia_serializable = fin_vigencia_serializable.isoformat()
        normalized_payload["fin_vigencia"] = fin_vigencia_serializable

    return await update("timbrados", id, normalized_payload, key="id")


async def obtener_secuencias_venta(
    filtros: dict,
    limite: int = 100,
    offset: int = 0,
):
    # filtros esperados: id_localfk, id_vendedorfk, id_timbradofk (opcional)
    return await get("secuencias_venta", filtros or {}, limit=limite, offset=offset, columns="*")


async def obtener_timbrado_vigente():
    # Regla: escoger timbrado con fin_vigencia > now() (y el mayor id si hay varios)
    now_utc = datetime.now(timezone.utc)

    # IMPORTANTE:
    # No se debe filtrar por igualdad exacta fin_vigencia == now,
    # porque casi nunca coinciden al mismo segundo/milisegundo.
    # En su lugar, cargamos timbrados y decidimos desde Python.
    filas = await get("timbrados", {}, limit=1000, offset=0, columns="*")

    vigente = None
    for t in filas:
        fv = t.get("fin_vigencia")
        if fv is None:
            continue
        try:
            fv_dt = fv if isinstance(fv, datetime) else datetime.fromisoformat(str(fv))
            if fv_dt.tzinfo is None:
                fv_dt = fv_dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        if fv_dt > now_utc:
            if vigente is None or int(t.get("id", 0)) > int(vigente.get("id", 0)):
                vigente = t

    if vigente is None:
        raise ValueError("No existe timbrado activo")
    return vigente


async def _obtener_or_crear_secuencia_venta(
    id_local: int,
    id_vendedor: int,
    id_timbrado: int,
) -> dict:
    """
    Asegura que retorne SIEMPRE:
      - id (PK de secuencias_venta)
      - ultimo_nro

    generic_crud puede no devolver todas las columnas en el INSERT; por eso,
    si el insert no retorna 'id', hacemos un GET posterior por la PK compuesta.
    """
    # 1) intentar obtener
    filas = await get(
        "secuencias_venta",
        {"id_localfk": id_local, "id_vendedorfk": id_vendedor, "id_timbradofk": id_timbrado},
        limit=1,
        offset=0,
        columns="id,ultimo_nro",
    )
    if filas:
        return filas[0]

    # 2) si no existe, insertar
    inserted = await insert(
        "secuencias_venta",
        {
            "id_localfk": id_local,
            "id_vendedorfk": id_vendedor,
            "id_timbradofk": id_timbrado,
            "ultimo_nro": 0,
        },
    )

    # Si el insert trajo 'id', úsalo; si no, hacemos GET posterior.
    if isinstance(inserted, dict) and inserted.get("id") is not None:
        return inserted

    filas = await get(
        "secuencias_venta",
        {"id_localfk": id_local, "id_vendedorfk": id_vendedor, "id_timbradofk": id_timbrado},
        limit=1,
        offset=0,
        columns="id,ultimo_nro",
    )
    if not filas:
        raise ValueError("No se pudo crear/recuperar secuencia_venta")
    return filas[0]


async def emitir_cod_num_venta(id_local: int, id_vendedor: int) -> dict:
    from src.infraestructura.config.supabase import get_supabase_client

    timbrado = await obtener_timbrado_vigente()
    id_timbrado = timbrado.get("id")

    if id_timbrado is None:
        raise ValueError("Timbrado vigente no tiene id")

    # Obtener códigos de local y vendedor
    locales = await get("locales", {"id": id_local}, limit=1, offset=0, columns="cod_num")
    vendedores = await get("vendedores", {"id": id_vendedor}, limit=1, offset=0, columns="cod_num")
    if not locales:
        raise ValueError(f"Local {id_local} no existe")
    if not vendedores:
        raise ValueError(f"Vendedor {id_vendedor} no existe")

    cod_local_raw = locales[0].get("cod_num") or "000"
    cod_vendedor_raw = vendedores[0].get("cod_num") or "000"

    # Extraer SOLO números (si vienen como "L01" / "V01", etc.)
    cod_local_digits = re.sub(r"\D", "", str(cod_local_raw)) or "0"
    cod_vendedor_digits = re.sub(r"\D", "", str(cod_vendedor_raw)) or "0"

    secuencia = await _obtener_or_crear_secuencia_venta(id_local, id_vendedor, id_timbrado)
    id_secuencia = secuencia.get("id")
    ultimo_nro = int(secuencia.get("ultimo_nro") or 0)

    nuevo = ultimo_nro + 1

    # Incremento persistido (UPDATE con PK compuesta)
    # Nota: sin lock/SQL atómico real, esto no es 100% seguro ante concurrencia.
    # Pero sí hacemos retry si el UPDATE no afectó filas.
    client = get_supabase_client()

    updated = (
        client.table("secuencias_venta")
        .update({"ultimo_nro": nuevo})
        .eq("id_localfk", id_local)
        .eq("id_vendedorfk", id_vendedor)
        .eq("id_timbradofk", id_timbrado)
        .execute()
    )

    if not getattr(updated, "data", None):
        # Si no existía (o no se afectó), creamos y volvemos a intentar una vez.
        await _obtener_or_crear_secuencia_venta(id_local, id_vendedor, id_timbrado)

        updated = (
            client.table("secuencias_venta")
            .update({"ultimo_nro": nuevo})
            .eq("id_localfk", id_local)
            .eq("id_vendedorfk", id_vendedor)
            .eq("id_timbradofk", id_timbrado)
            .execute()
        )

        if not getattr(updated, "data", None):
            raise ValueError("No se pudo actualizar secuencias_venta. (PK compuesta no encontrada)")

    cod_num_completo = (
        str(cod_local_digits).zfill(3)
        + "-"
        + str(cod_vendedor_digits).zfill(3)
        + "-"
        + str(nuevo).zfill(7)
    )

    return {
        "cod_num_completo": cod_num_completo,
        "id_secuencia": id_secuencia,
        "id_timbrado": id_timbrado,
        "secuencia": nuevo,
    }
