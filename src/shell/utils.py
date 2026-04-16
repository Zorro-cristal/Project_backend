from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional, Union

def prepare_payload_for_db(
    data: Union[Any, Dict],
    exclude_fields: Optional[list[str]] = None
) -> Dict:
    """
    Convierte una instancia de dataclass o un diccionario en un diccionario
    apto para operaciones de base de datos.
    Excluye el campo 'id' y cualquier campo especificado en 'exclude_fields'.
    """
    if is_dataclass(data):
        payload = asdict(data)
    else:
        payload = dict(data) # Asegura que sea un dict mutable

    payload.pop("id", None) # El 'id' se maneja por separado (en la URL, etc.)

    if exclude_fields:
        for field in exclude_fields:
            payload.pop(field, None)

    return payload

def filter_none_values(data: Dict) -> Dict:
    """
    Filtra un diccionario para remover entradas donde el valor es None.
    Útil para actualizaciones parciales (PATCH) donde solo se envían los campos modificados.
    """
    return {k: v for k, v in data.items() if v is not None}