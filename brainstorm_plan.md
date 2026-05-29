# Brainstorm Plan (Venta + detalle_venta endpoints)

## Información observada
- `src/infraestructura/api/venta_api.py` actualmente expone:
  - `PUT /venta/{id}` y `PATCH /venta/{id}` para actualizar
  - `POST /venta/` para crear
  - `GET /venta/` para listar con filtros
  - `GET /venta/{id}` para obtener una venta (usa `obtener_ventas` y devuelve `result[0]` si list)
- Existe `src/infraestructura/api/detalle_venta_api.py` con:
  - `GET /detalle_venta/` (filtros)
  - `GET /detalle_venta/{id}` (un detalle)
- `src/infraestructura/services/venta_service.py` ya implementa `attach_related_data(ventas)` que arma `usuario`, `cliente`, `local` y `detalles` (usando `obtenerDetalleVenta` con `id_ventafk`).
- `src/infraestructura/services/detalle_venta_service.py` implementa `obtener_detalle_ventas(filtros)` con `attach_related_data` que además carga el `producto` dentro de cada detalle.

## Objetivo
Implementar endpoints análogos a “los endpoints pero para venta” que permitan:
1. `GET /venta/{id}` → devolver solo la venta
2. `GET /venta/{id}?include=detalleVenta` → devolver venta + `detalleVenta`
3. `GET /venta/{id}/detalleVenta` → devolver solo `detalle_venta`

## Consideraciones de diseño
- Actualmente `venta_service.obtener_ventas()` devuelve ventas **con detalles** ya adjuntados (`venta['detalles']`).
- Para respetar el contrato:
  - `GET /venta/{id}` sin include debe devolver solo la venta (sin `detalles`).
  - `GET /venta/{id}?include=detalleVenta` debe devolver venta con detalles.
- Como el service actual siempre adjunta `detalles`, habrá que ajustar a nivel API o crear una variante service que no adjunte detalles.

## Plan propuesto
### A) Cambios en `src/infraestructura/api/venta_api.py`
1. Modificar `obtenerVentaPorIdApi` para aceptar query param:
   - `include: Optional[str] = Query(None, description='...')`
2. Lógica:
   - Si `include == 'detalleVenta'`:
     - usar `obtener_ventas({'id': id})` y devolver el registro completo (incluye `detalles`).
   - Si `include` es None o no coincide:
     - recuperar solo la venta sin adjuntar detalles.
     - Para esto, no deberíamos reutilizar directamente `obtener_ventas`.
     - Opción 1 (preferida): agregar un método en `venta_service` que llame a `obtenerVenta` del repository sin `attach_related_data`.
     - Opción 2: usar `obtener_ventas` y luego eliminar `detalles` del objeto antes de retornar.
       - Esto mantiene cambios mínimos pero “carga de más”.

3. Agregar nuevo endpoint:
   - `@router.get("/{id}/detalleVenta", summary="Obtener detalle_venta por venta")`
   - Llamar a `obtener_detalle_ventas({'id_ventafk': id})`
   - devolver la lista.

### B) Si se requiere (para evitar cargar relaciones)
- Añadir en `src/infraestructura/services/venta_service.py` una función:
  - `async def obtener_venta_por_id(filtros: dict=None, columnas='*')` que llame a `obtenerVenta` (repository) sin `attach_related_data`.

## Archivos dependientes a editar
- `src/infraestructura/api/venta_api.py`
- Posible: `src/infraestructura/services/venta_service.py`

## Followup steps
- Ejecutar un smoke test:
  - levantar la app (si existe comando) y/o ejecutar tests.
- Probar endpoints:
  - `GET /venta/1`
  - `GET /venta/1?include=detalleVenta`
  - `GET /venta/1/detalleVenta`

## Validación
- Asegurar que la clave de relación que el service actual usa para adjuntar detalles es `detalles`.
- Confirmar naming requerido: el contrato menciona `detalleVenta`; internamente el campo podría ser `detalles`. Se puede mapear al nombre que el frontend espera.

