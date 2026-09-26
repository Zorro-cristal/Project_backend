from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timezone
from typing import Any, Callable

from src.infraestructura.config.turso import get_turso_connection

TABLE_PRIMARY_KEYS: dict[str, str] = {
    "personas": "cedula",
    "roles": "id",
    "permisos": "id",
    "permisos_roles": "id",
    "marcas": "id",
    "categorias": "id",
    "precios": "id",
    "productos": "id",
    "detalles_producto": "cod_barra",
    "detalles_precio": "id",
    "ingredientes": "id",
    "usuarios": "id",
    "proveedores": "id",
    "clientes": "id",
    "vendedores": "id",
    "locales": "id",
    "mesas": "id",
    "stocks": "id",
    "cajas": "id",
    "timbrados": "id",
    "secuencias_venta": "id",
    "ventas": "id",
    "detalle_venta": "id",
    "compras": "id",
    "detalle_compra": "id_detalle_compra",
    "egresos": "id",
    "ordenes": "id",
    "reservas": "id",
    "cuotas_venta": "id",
    "pagos_venta": "id",
    "cuotas_compra": "id",
    "pagos_compra": "id",
}

# (tabla principal, nombre de relación) -> (tabla relacionada, columna principal,
# columna relacionada, relación de uno a muchos).
RELATIONSHIPS: dict[tuple[str, str], tuple[str, str, str, bool]] = {
    ("productos", "marcas"): ("marcas", "id_marcafk", "id", False),
    ("productos", "detalles_producto"): ("detalles_producto", "id", "id_productofk", True),
    ("detalles_producto", "productos"): ("productos", "id_productofk", "id", False),
    ("detalles_producto_con_stock", "productos"): ("productos", "id_productofk", "id", False),
    ("detalles_producto", "detalles_precio"): ("detalles_precio", "cod_barra", "id_detalleproductofk", True),
    ("detalles_producto_con_stock", "detalles_precio"): ("detalles_precio", "cod_barra", "id_detalleproductofk", True),
    ("detalles_precio", "precios"): ("precios", "id_preciofk", "id", False),
    ("detalles_precio", "id_preciofk"): ("precios", "id_preciofk", "id", False),
    ("detalles_precio", "detalles_producto"): ("detalles_producto", "id_detalleproductofk", "cod_barra", False),
    ("precios", "detalles_precio"): ("detalles_precio", "id", "id_preciofk", True),
    ("permisos_roles", "permisos"): ("permisos", "id_permisofk", "id", False),
    ("permisos_roles", "roles"): ("roles", "id_rolfk", "id", False),
    ("usuarios", "personas"): ("personas", "id_personafk", "cedula", False),
    ("usuarios", "roles"): ("roles", "id_rolfk", "id", False),
    ("vendedores", "usuarios"): ("usuarios", "id_usuariofk", "id", False),
    ("cajas", "usuarios"): ("usuarios", "id_usuariofk", "id", False),
    ("clientes", "personas"): ("personas", "id_personafk", "cedula", False),
    ("proveedores", "personas"): ("personas", "id_personafk", "cedula", False),
    ("mesas", "locales"): ("locales", "id_localfk", "id", False),
    ("ordenes", "mesas"): ("mesas", "id_mesafk", "id", False),
    ("egresos", "cajas"): ("cajas", "id_cajafk", "id", False),
}

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_EXACT_JOIN_FIELDS = {"alias", "nombre", "nombres", "ruc", "razon_social"}


def _identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Identificador SQL no válido: {value!r}")
    return f'"{value}"'


def _split_projection(projection: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(projection):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"Proyección inválida: {projection!r}")
        elif char == "," and depth == 0:
            parts.append(projection[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError(f"Proyección inválida: {projection!r}")
    final = projection[start:].strip()
    if final:
        parts.append(final)
    return parts


def _parse_projection_item(item: str) -> tuple[str, str, list[str] | None, bool]:
    opening = item.find("(")
    alias_separator = item.find(":")
    if alias_separator >= 0 and (opening < 0 or alias_separator < opening):
        alias = item[:alias_separator].strip()
        selector = item[alias_separator + 1 :].strip()
        has_alias = True
    else:
        alias = item.strip()
        selector = alias
        has_alias = False

    if "(" not in selector:
        field = selector.strip()
        if not _IDENTIFIER.fullmatch(field) and field != "*":
            raise ValueError(f"Columna no válida en proyección: {field!r}")
        return alias if has_alias else field, field, None, False

    relation, remainder = selector.split("(", 1)
    if not remainder.endswith(")"):
        raise ValueError(f"Proyección de relación inválida: {item!r}")
    inner = "!inner" in relation
    relation = relation.split("!", 1)[0].strip()
    if not _IDENTIFIER.fullmatch(relation):
        raise ValueError(f"Relación no válida en proyección: {relation!r}")
    return alias if has_alias else relation, relation, _split_projection(remainder[:-1]), inner


def _relationship(table: str, relation: str) -> tuple[str, str, str, bool]:
    try:
        return RELATIONSHIPS[(table, relation)]
    except KeyError as error:
        raise ValueError(
            f"No hay una relación Turso declarada para {table}.{relation}; "
            "agrega el vínculo en RELATIONSHIPS."
        ) from error


def _db_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bool):
        return int(value)
    return value


def _fetch_dicts(connection: Any, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cursor = connection.execute(sql, tuple(_db_value(value) for value in parameters))
    if not cursor.description:
        return []
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def _filter_sql(
    table: str,
    filters: dict[str, Any] | None,
) -> tuple[list[str], list[Any]]:
    clauses: list[str] = []
    values: list[Any] = []
    for field, value in (filters or {}).items():
        if "mostrar_inactivo" in field:
            if value == 0:
                clauses.append('"estado" != ?')
                values.append(0)
            continue

        if "." in field:
            relation_name, related_field = field.split(".", 1)
            related_table, source_key, related_key, _ = _relationship(table, relation_name)
            nested_clauses, nested_values = _single_filter(related_field, value, "related")
            clauses.append(
                f"EXISTS (SELECT 1 FROM {_identifier(related_table)} AS related "
                f"WHERE related.{_identifier(related_key)} = {_identifier(table)}.{_identifier(source_key)} "
                f"AND {' AND '.join(nested_clauses)})"
            )
            values.extend(nested_values)
            continue

        field_name = field
        operator = "="
        if field.endswith("_inicio"):
            field_name, operator = field.removesuffix("_inicio"), ">="
        elif field.endswith("_fin"):
            field_name, operator = field.removesuffix("_fin"), "<="
        elif field.endswith("_mayor_que"):
            field_name, operator = field.removesuffix("_mayor_que"), ">"
        field_sql = _identifier(field_name)

        if isinstance(value, (list, tuple, set)):
            items = list(value)
            if not items:
                clauses.append("0 = 1")
                continue
            placeholders = ", ".join("?" for _ in items)
            clauses.append(f"{field_sql} IN ({placeholders})")
            values.extend(items)
        elif value is None:
            clauses.append(f"{field_sql} IS NULL" if operator == "=" else f"{field_sql} {operator} NULL")
        else:
            clauses.append(f"{field_sql} {operator} ?")
            values.append(value)
    return clauses, values


def _single_filter(field: str, value: Any, table_alias: str) -> tuple[list[str], list[Any]]:
    column = f"{table_alias}.{_identifier(field)}"
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        if not items:
            return ["0 = 1"], []
        return [f"{column} IN ({', '.join('?' for _ in items)})"], items
    if value is None:
        return [f"{column} IS NULL"], []
    return [f"{column} = ?"], [value]


def _hydrate_relations(
    connection: Any,
    table: str,
    records: list[dict[str, Any]],
    projection: str,
    depth: int = 0,
) -> list[dict[str, Any]]:
    if depth > 6:
        raise ValueError("La proyección excede la profundidad máxima de relaciones (6).")

    projection_items = _split_projection(projection or "*")
    include_all = "*" in projection_items
    scalar_items: list[tuple[str, str]] = []
    relation_items: list[tuple[str, str, list[str], bool]] = []
    for item in projection_items:
        output_name, source_name, nested, is_inner = _parse_projection_item(item)
        if nested is None:
            if source_name != "*":
                scalar_items.append((output_name, source_name))
        else:
            relation_items.append((output_name, source_name, nested, is_inner))

    result: list[dict[str, Any]] = []
    for record in records:
        projected = dict(record) if include_all else {
            output: record.get(source) for output, source in scalar_items
        }
        result.append(projected)

    for output_name, relation_name, nested_items, is_inner in relation_items:
        related_table, source_key, related_key, is_many = _relationship(table, relation_name)
        parent_values = list(dict.fromkeys(
            record.get(source_key) for record in records if record.get(source_key) is not None
        ))
        related_records: list[dict[str, Any]] = []
        related_keys: list[Any] = []
        if parent_values:
            placeholders = ", ".join("?" for _ in parent_values)
            related_records = _fetch_dicts(
                connection,
                f"SELECT * FROM {_identifier(related_table)} "
                f"WHERE {_identifier(related_key)} IN ({placeholders})",
                tuple(parent_values),
            )
            related_keys = [related_record.get(related_key) for related_record in related_records]
            related_records = _hydrate_relations(
                connection,
                related_table,
                related_records,
                ", ".join(nested_items) or "*",
                depth + 1,
            )

        related_map: dict[Any, list[dict[str, Any]]] = {}
        for related_key_value, related_record in zip(related_keys, related_records):
            related_map.setdefault(related_key_value, []).append(related_record)

        for index, source_record in enumerate(records):
            matches = related_map.get(source_record.get(source_key), [])
            result[index][output_name] = matches if is_many else (matches[0] if matches else None)

        if is_inner:
            result = [row for row in result if row.get(output_name)]

    return result


def _with_connection(operation: Callable[[Any], Any]) -> Any:
    connection = get_turso_connection()
    try:
        result = operation(connection)
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _sync_update(connection: Any, table: str, row_id: Any, updates: dict[str, Any], key: str) -> dict[str, Any]:
    if not updates:
        existing = _fetch_dicts(
            connection,
            f"SELECT * FROM {_identifier(table)} WHERE {_identifier(key)} = ? LIMIT 1",
            (row_id,),
        )
        if existing:
            return existing[0]
        raise LookupError(f"No se encontró registro con {key} {row_id} en {table}")

    assignments = ", ".join(f"{_identifier(field)} = ?" for field in updates)
    params = tuple(updates.values()) + (row_id,)
    connection.execute(
        f"UPDATE {_identifier(table)} SET {assignments} WHERE {_identifier(key)} = ?",
        tuple(_db_value(value) for value in params),
    )
    rows = _fetch_dicts(
        connection,
        f"SELECT * FROM {_identifier(table)} WHERE {_identifier(key)} = ? LIMIT 1",
        (row_id,),
    )
    if not rows:
        raise LookupError(f"No se encontró registro con {key} {row_id} en {table}")
    return rows[0]


async def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    payload = dict(data)
    primary_key = TABLE_PRIMARY_KEYS.get(table)
    if table != "secuencias_venta" and (
        "fecha_creado" not in payload or payload["fecha_creado"] is None
    ):
        payload["fecha_creado"] = datetime.now(timezone.utc).isoformat()

    def operation(connection: Any) -> dict[str, Any]:
        if primary_key and payload.get(primary_key) is not None:
            existing = _fetch_dicts(
                connection,
                f"SELECT * FROM {_identifier(table)} WHERE {_identifier(primary_key)} = ? LIMIT 1",
                (payload[primary_key],),
            )
            if existing:
                return _sync_update(connection, table, payload[primary_key], payload, primary_key)

        fields = list(payload)
        field_sql = ", ".join(_identifier(field) for field in fields)
        placeholders = ", ".join("?" for _ in fields)
        cursor = connection.execute(
            f"INSERT INTO {_identifier(table)} ({field_sql}) VALUES ({placeholders})",
            tuple(_db_value(payload[field]) for field in fields),
        )
        if primary_key and payload.get(primary_key) is not None:
            row_id = payload[primary_key]
            key = primary_key
        elif cursor.lastrowid is not None:
            row_id, key = cursor.lastrowid, primary_key
        else:
            return payload
        rows = _fetch_dicts(
            connection,
            f"SELECT * FROM {_identifier(table)} WHERE {_identifier(key)} = ? LIMIT 1",
            (row_id,),
        )
        if not rows:
            raise RuntimeError(f"Se insertó en {table}, pero no se pudo recuperar la fila creada.")
        return rows[0]

    return await asyncio.to_thread(_with_connection, operation)


async def get(
    table: str,
    filters: dict[str, Any] | None = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str | None = None,
    order_desc: bool = True,
    columns: str = "*",
    joins: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    def operation(connection: Any) -> list[dict[str, Any]]:
        clauses, parameters = _filter_sql(table, filters)

        for join_config in joins or []:
            join_table = join_config.get("table")
            foreign_key = join_config.get("foreign_key")
            primary_key = join_config.get("primary_key", "id")
            name_field = join_config.get("name_field")
            name_filter = join_config.get("nombre_usuario")
            if not all((join_table, foreign_key, name_field)) or name_filter is None:
                continue

            comparison = "=" if name_field in _EXACT_JOIN_FIELDS else "LIKE"
            match_value = name_filter if comparison == "=" else f"%{name_filter}%"
            related_ids = _fetch_dicts(
                connection,
                f"SELECT {_identifier(primary_key)} FROM {_identifier(join_table)} "
                f"WHERE {_identifier(name_field)} {comparison} ? COLLATE NOCASE",
                (match_value,),
            )
            id_values = [row[primary_key] for row in related_ids]
            if not id_values:
                return []
            clauses.append(
                f"{_identifier(foreign_key)} IN ({', '.join('?' for _ in id_values)})"
            )
            parameters.extend(id_values)

        sql = f"SELECT * FROM {_identifier(table)}"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        if order_by:
            order_fields = [f"{_identifier(order_by)} {'DESC' if order_desc else 'ASC'}"]
            if "id" not in order_by and table not in {
                "detalles_producto",
                "detalles_producto_con_stock",
                "personas",
            }:
                order_fields.append(f'"id" {"DESC" if order_desc else "ASC"}')
            sql += " ORDER BY " + ", ".join(order_fields)
        sql += " LIMIT ? OFFSET ?"
        parameters.extend((-1 if limit is None else max(0, limit), max(0, offset)))
        records = _fetch_dicts(connection, sql, tuple(parameters))
        return _hydrate_relations(connection, table, records, columns)

    return await asyncio.to_thread(_with_connection, operation)


async def update(
    table: str,
    id: Any,
    updates: dict[str, Any],
    key: str = "id",
) -> dict[str, Any]:
    return await asyncio.to_thread(
        _with_connection,
        lambda connection: _sync_update(connection, table, id, updates, key),
    )


async def increment(table: str, id: Any, column: str, key: str = "id") -> dict[str, Any]:
    """Incrementa atómicamente una columna entera y devuelve la fila resultante."""
    def operation(connection: Any) -> dict[str, Any]:
        rows = _fetch_dicts(
            connection,
            f"UPDATE {_identifier(table)} "
            f"SET {_identifier(column)} = COALESCE({_identifier(column)}, 0) + 1 "
            f"WHERE {_identifier(key)} = ? RETURNING *",
            (id,),
        )
        if not rows:
            raise LookupError(f"No se encontró registro con {key} {id} en {table}")
        return rows[0]

    return await asyncio.to_thread(_with_connection, operation)


async def soft_delete(table: str, id: Any) -> dict[str, Any]:
    return await update(table, id, {"estado": 0})


async def count(table: str, filters: dict[str, Any] | None = None) -> int:
    def operation(connection: Any) -> int:
        clauses, parameters = _filter_sql(table, filters)
        sql = f"SELECT COUNT(*) AS total FROM {_identifier(table)}"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        rows = _fetch_dicts(connection, sql, tuple(parameters))
        return int(rows[0]["total"]) if rows else 0

    return await asyncio.to_thread(_with_connection, operation)
