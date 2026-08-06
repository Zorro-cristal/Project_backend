from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union


def _is_json_primitive(value: Any) -> bool:
    """Permite que viaje a Supabase solo lo que típicamente es serializable."""
    return value is None or isinstance(value, (str, int, float, bool))


def prepararPayloadDb(
    data: Union[Any, Dict],
    exclude_fields: Optional[list[str]] = None,
) -> Dict:
    """Convierte una dataclass o dict en un payload apto para Supabase.

    Además de excluir 'id' y campos del parámetro `exclude_fields`, elimina
    automáticamente atributos cuyo valor sea otro objeto (p.ej. Rol/Persona)
    para evitar errores tipo:
      "Could not find the '<campo>' column of '<tabla>' ..."

    Resultado: solo viajan primitives (str/int/float/bool/None) y campos FK
    (id_*) que normalmente ya son int/str.

    Nota: para evitar violaciones NOT NULL, este helper NO envía campos con
    valor None si existen en el payload.
    """

    if is_dataclass(data):
        payload = asdict(data)
    else:
        payload = dict(data)  # Asegura que sea un dict mutable

    # Evita violaciones NOT NULL en BD: no mandes claves con valor None.
    for key in list(payload.keys()):
        if payload[key] is None:
            payload.pop(key, None)

    # El 'id' se maneja por separado (en la URL, etc.)
    payload.pop("id", None)

    if exclude_fields:
        for field in exclude_fields:
            payload.pop(field, None)

    # Ajuste para fechas: si vienen como datetime, conviértelos a ISO string
    # antes de aplicar el filtro de primitividad.
    for key in ("valido_desde", "valido_hasta", "fecha", "fecha_cierre", "fecha_creado"):
        if key in payload and isinstance(payload[key], datetime):
            payload[key] = payload[key].isoformat()
        # También convertir cualquier campo datetime que venga como objeto con isoformat
        elif key in payload and hasattr(payload[key], "isoformat"):
            payload[key] = payload[key].isoformat()

    # Filtro global: remueve campos cuyo valor sea un objeto/dict/list anidado.
    # (Esto evita que 'rol': {..} o 'persona': {..} se manden como columna.)
    for key in list(payload.keys()):
        if not _is_json_primitive(payload[key]):
            payload.pop(key, None)

    return payload


def normalizar_booleanos(
    payload: dict,
    boolean_fields: list[str],
    on_insert: bool = True,
) -> dict:
    """Convierte valores booleanos a enteros y normaliza None para inserciones."""
    for field in boolean_fields:
        if field in payload:
            if isinstance(payload[field], bool):
                payload[field] = 1 if payload[field] else 0
            elif payload[field] is None and on_insert:
                payload[field] = 0
    return payload


async def attach_related(
    items: list[dict],
    fk_field: str,
    fetch_func,
    fetch_filter_name: str = "id",
    related_key_field: str = "id",
    output_field: str | None = None,
) -> list[dict]:
    """Adjunta objetos relacionados a una colección de registros.

    - `items`: lista de dicts que contienen la FK (ej. `id_usuariofk`).
    - `fk_field`: campo en `items` que guarda la FK.
    - `fetch_func`: coroutine que recibe un dict de filtros y devuelve lista de dicts relacionados.
    - `fetch_filter_name`: nombre del campo de filtro que espera `fetch_func` (por ejemplo, 'id' o 'cedula').
    - `related_key_field`: campo en los objetos relacionados que corresponde al valor de FK.
    - `output_field`: nombre del campo a crear en cada item con el objeto relacionado. Si es None
      se deriva eliminando prefijos `id_` y sufijos `fk` del `fk_field`.

    Devuelve la lista `items` con los objetos relacionados insertados (no crea copias profundas).
    """
    if not items:
        return items

    ids = {item.get(fk_field) for item in items if item.get(fk_field)}
    if not ids:
        return items

    filtros = {fetch_filter_name: list(ids)}
    related = await fetch_func(filtros)

    related_map = {rel.get(related_key_field): rel for rel in (related or [])}

    if output_field is None:
        name = fk_field
        if isinstance(name, str):
            name = name.removeprefix("id_").removesuffix("fk")
        output_field = name

    for item in items:
        key = item.get(fk_field)
        item[output_field] = related_map.get(key)

    return items


async def attach_grouped(
    items: list[dict],
    parent_id_field: str,
    fetch_func,
    fetch_filter_name: str,
    child_parent_field: str,
    output_field: str,
) -> list[dict]:
    """Adjunta listas de objetos relacionados (one-to-many) agrupadas por parent id.

    - `items`: lista de dicts que tienen el `parent_id_field` (normalmente 'id').
    - `parent_id_field`: campo en `items` que identifica al padre (ej. 'id').
    - `fetch_func`: coroutine que recibe un dict de filtros y devuelve lista de hijos.
    - `fetch_filter_name`: nombre del filtro que espera `fetch_func` (ej. 'id_comprafk').
    - `child_parent_field`: campo en los hijos que referencia al padre (ej. 'id_comprafk').
    - `output_field`: nombre del campo donde se pegará la lista de hijos en cada item.
    """
    if not items:
        return items

    parent_ids = {item.get(parent_id_field) for item in items if item.get(parent_id_field) is not None}
    if not parent_ids:
        for item in items:
            item[output_field] = []
        return items

    filtros = {fetch_filter_name: list(parent_ids)}
    children = await fetch_func(filtros)

    grouped: dict = {}
    for child in (children or []):
        pid = child.get(child_parent_field)
        if pid is None:
            continue
        grouped.setdefault(pid, []).append(child)

    for item in items:
        pid = item.get(parent_id_field)
        item[output_field] = grouped.get(pid, [])

    return items


def filtrar_por_nombre_completo(
    items: list[dict],
    nombre_completo: str,
    path: list[str] | None = None,
) -> list[dict]:
    """Filtra una lista de registros por nombre completo de la persona asociada.

    - `items`: lista de dicts que representan los registros (ej. clientes, usuarios).
    - `nombre_completo`: texto con el que se compara (búsqueda por contenido, sin
      distinguir mayúsculas/minúsculas ni acentos).
    - `path`: ruta (lista de claves) hacia el objeto persona dentro de cada item.
      Ejemplos:
        - `['persona']` para un item que tiene `item['persona']`.
        - `['usuario', 'persona']` para un item con `item['usuario']['persona']`.
Si es None o vacío, se busca directamente en `item['nombres']` y `item['apellidos']`.

    Coincide si el texto (o cada palabra del texto) aparece dentro de
    "nombres apellidos" o "apellidos nombres". Si el texto tiene varias
    palabras (ej. "Juan Perez"), todas deben estar presentes en el nombre
    completo, sin importar el orden.
    """
    if not items or not nombre_completo:
        return items

    q = _normalizar_texto(nombre_completo)
    # Si trae varias palabras, usamos coincidencia por tokens (todas presentes).
    tokens = [t for t in q.split() if t]

    def _get_persona(item: dict) -> dict | None:
        cur = item
        for key in (path or []):
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return None
        return cur if isinstance(cur, dict) else None

    filtrados = []
    for item in items:
        persona = _get_persona(item) if path else item
        if not isinstance(persona, dict):
            continue

        nombres = _normalizar_texto(persona.get('nombres') or '')
        apellidos = _normalizar_texto(persona.get('apellidos') or '')

        combinado = f"{nombres} {apellidos}".strip()

        if len(tokens) > 1:
            # Todas las palabras del texto deben aparecer (en cualquier orden).
            if all(tok in combinado for tok in tokens):
                filtrados.append(item)
        else:
            # Búsqueda simple por contenido.
            if tokens and tokens[0] in combinado:
                filtrados.append(item)

    return filtrados


def _normalizar_texto(value: str) -> str:
    """Normaliza un texto para búsqueda: minúsculas y sin acentos."""
    import unicodedata

    texto = value.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto


async def validar_fk_existente(
    fk_value: Any,
    fetch_func,
    fetch_filter_name: str = "id",
    error_message: str | None = None,
) -> None:
    """Verifica que un valor de clave foránea exista en la entidad relacionada.

    - `fk_value`: valor de la FK a validar.
    - `fetch_func`: función asíncrona que recibe filtros y devuelve la lista de entidades relacionadas.
    - `fetch_filter_name`: nombre del campo de filtro que espera `fetch_func`.
    - `error_message`: mensaje de error personalizado para ValueError.
    """
    if fk_value is None:
        return

    registros = await fetch_func({fetch_filter_name: [fk_value]})
    if not registros:
        raise ValueError(error_message or f"Referencia inválida: {fk_value}")
