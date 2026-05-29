# TODO

- [x] Aplicar fix: agregar `id_rolfk` al dataclass `Usuario` para que se incluya en el payload DB.
- [x] Asegurar que `usuario_service.build_usuario_entity()` no descarte `id_rolfk`.
- [ ] Validar que `prepararPayloadDb` no elimine `id_rolfk` (debe ser primitiva int).
- [ ] Ejecutar pruebas/validación manual: crear usuario con payload que incluya `id_rolfk: 1`.


