from dataclasses import asdict, is_dataclass
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
    """

    if is_dataclass(data):
        payload = asdict(data)
    else:
        payload = dict(data)  # Asegura que sea un dict mutable

    # El 'id' se maneja por separado (en la URL, etc.)
    payload.pop("id", None)

    if exclude_fields:
        for field in exclude_fields:
            payload.pop(field, None)

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
