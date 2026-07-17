-- ============================================================
-- 1. PERSONAS (15 Registros - Base Intacta)
-- ============================================================
INSERT INTO personas (cedula, nombres, apellidos, telefono, direccion, nacionalidad) VALUES
(1000001, 'Administrador', 'Root', 981000001, 'Centro, Villarrica', 'PRY'),
(1000002, 'Ana', 'Britez', 971000002, 'Bvr. Yegros, Villarrica', 'PRY'),
(1000003, 'Luis', 'Giménez', 961000003, 'Barrio Ybaroty, Villarrica', 'PRY'),
(1000004, 'Marta', 'Ruiz', 982000004, 'Barrio Estación, Villarrica', 'PRY'),
(1000005, 'Diego', 'Ortiz', 991000005, 'Ruta 8, Mbocayaty', 'PRY'),
(2000001, 'Distribuidora', 'Guairá S.A.', 2100001, 'Acceso Sur, Ñemby', 'PRY'),
(2000002, 'Frigorífico', 'Villarrica', 2100002, 'Ruta 8, Villarrica', 'PRY'),
(2000003, 'Bebidas Unidas', 'S.R.L.', 2100003, 'Asunción', 'PRY'),
(2000004, 'Insumos', 'Gastronómicos', 2100004, 'San Lorenzo', 'PRY'),
(2000005, 'Granja', 'Avícola San José', 2100005, 'Colonia Independencia', 'PRY'),
(3000001, 'Juan', 'Pérez', 981333333, 'Centro, Villarrica', 'PRY'),
(3000002, 'María', 'López', 971333333, 'Barrio San Miguel, Villarrica', 'PRY'),
(3000003, 'Carlos', 'Gómez', 961333333, 'Felix Perez Cardozo', 'PRY'),
(3000004, 'Empresa', 'Constructora XYZ', 21333333, 'Villarrica', 'PRY'),
(3000005, 'Cliente', 'Ocasional', null, 'Sin especificar', 'PRY');

-- ============================================================
-- 2. ROLES, PERMISOS Y USUARIOS (5 Usuarios)
-- ============================================================
INSERT INTO roles (id, nombre, observacion, estado) VALUES
(1, 'Admin', 'Acceso Total', 1), (2, 'Cajero', 'Caja y Cobros', 1),
(3, 'Mozo', 'Atención en salón', 1), (4, 'Gerente', 'Reportes y auditoría', 1),
(5, 'Cocinero', 'Visualización de comandas', 1);

INSERT INTO permisos (id, nombre) VALUES 
(1, 'Facturación'), (2, 'Inventario'), (3, 'Usuarios'), (4, 'Reportes'), (5, 'Compras');

INSERT INTO permisos_roles (crear, editar, eliminar, leer, id_permisofk, id_rolfk) VALUES
(true, true, true, true, 1, 1), (true, true, true, true, 2, 1),
(true, false, false, true, 1, 2), (false, false, false, true, 2, 2),
(true, true, false, true, 1, 3);

INSERT INTO "public"."usuarios" ("id", "contra", "alias", "estado", "fecha_creado", "id_rolfk", "id_personafk") VALUES 
(1, 'scrypt$pQDitONnZE/sjyQuLA373w==$3qTf0pWmVEm36W5957vaqUXTmH8dTbjsB65un1+sd3o=', 'admin', 1, '2026-07-04 15:17:08.935272+00', 1, 1000001),
(2, 'scrypt$wYqY5zrKgamMvne3Hz6ZNg==$TDxeVqjuOEQBcqCcn+tqZQh2Dm5UvaQjf8rJbzDD7eY=', 'ana_caja', 1, '2026-07-04 15:17:09.30662+00', 2, 1000002),
(3, 'scrypt$ky8MgYQXw+VquxN0UAVIJw==$K5wt85o6hLInbu0r/Gj2i1ZzeNi3zBaYUhdtw0ADuJc=', 'luis_caja2', 1, '2026-07-04 15:17:09.557405+00', 2, 1000003),
(4, 'scrypt$xEsISuHV67XSfLqsgOdRTw==$8044bJlqnJYRAJzjN2/zD3ZtPM/PZTSzor5CHZJ1Jnc=', 'marta_mozo', 1, '2026-07-04 15:17:09.826143+00', 3, 1000004),
(5, 'scrypt$YhNDBgTevJhqpM3vptf+qw==$qx/IxjhsVaG7hm/ouk6/fHQJIog6ieM4MszlyQEzZMM=', 'diego_mozo', 1, '2026-07-04 15:17:10.076216+00', 3, 1000005);

-- ============================================================
-- 1. PERSONAS (Combos: Todo lleno, todo nulo, solo teléfono, solo direc/nac)
-- ============================================================
INSERT INTO personas (cedula, nombres, apellidos, telefono, direccion, nacionalidad) VALUES
(1234567, 'Juan', 'Perez', 981123456, 'Centro, Villarrica', 'PRY'),
(2345678, 'Maria', 'Gomez', NULL, NULL, NULL),
(3456789, 'Carlos', 'Lopez', 971654321, NULL, 'PRY'),
(4567890, 'Ana', 'Britez', NULL, 'Barrio Ybaroty', NULL);

-- ============================================================
-- 5. MARCAS
-- ============================================================
INSERT INTO marcas (id, nombre, estado) VALUES 
(1, 'Coca Cola', 1), (2, 'Lactolanda', 1), (3, 'Propia', 1), (4, 'Generica', 0);

-- ============================================================
-- 6. CATEGORIAS (Combos: con/sin descripción)
-- ============================================================
INSERT INTO categorias (id, nombre, descripcion, estado) VALUES 
(1, 'Bebidas', 'Bebidas frías', 1), 
(2, 'Comidas', NULL, 1), 
(3, 'Insumos', 'Materia prima', 1),
(4, 'Postres', NULL, 1);

-- ============================================================
-- 7. PRECIOS (Combos: Sin fin, con fin futuro, con fin pasado)
-- ============================================================
INSERT INTO precios (id, monto, valido_desde, valido_hasta) VALUES
(1, 15000, '2023-01-01 00:00:00-03', NULL), -- Siempre vigente
(2, 12000, '2023-01-01 00:00:00-03', '2023-12-31 23:59:59-03'), -- Vencido
(3, 35000, '2024-01-01 00:00:00-03', NULL),
(4, 10000, '2026-07-01 00:00:00-03', '2026-12-31 23:59:59-03'); -- Promoción activa

-- ============================================================
-- 8. PRODUCTOS (Combos es_comida / es_ingrediente y opcionales)
-- ============================================================
INSERT INTO productos (id, nombre, descripcion, estado, impuesto, pesable, perecedero, costeo, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES
(1, 'Hamburguesa', 'Doble carne', 1, 10, false, true, 15000, 'Unidad', false, true, 2, 3),  -- F/T: Solo Comida
(2, 'Carne Molida', NULL, 1, 5, true, true, 35000, 'Kg', true, false, 3, 3),              -- T/F: Solo Ingrediente
(3, 'Masa Pre-lista', 'Masa madre', 1, 5, true, true, NULL, 'Kg', true, true, 3, 3),      -- T/T: Comida que tmb es ingrediente
(4, 'Gaseosa 500ml', NULL, 1, 10, false, false, 4500, 'Unidad', false, false, 1, 1),      -- F/F: Producto normal
(5, 'Servilletas', NULL, 1, 10, false, false, NULL, 'Unidad', NULL, NULL, 3, 4);          -- NULL/NULL: Insumo no comestible

-- ============================================================
-- 9. DETALLES PRODUCTO (Combos: Todo lleno, ambos nulos, 1 nulo)
-- ============================================================
INSERT INTO detalles_producto (cod_barra, unidad_por_lote, color, tamanho, id_productofk) VALUES
('BAR001', 1, 'Marrón', 200, 1),  -- Lleno
('BAR002', 10, NULL, NULL, 2),    -- Nulos
('BAR003', 24, NULL, 500, 4),     -- Solo tamaño
('BAR004', 50, 'Blanco', NULL, 5);-- Solo color

-- ============================================================
-- 10. DETALLES PRECIO
-- ============================================================
INSERT INTO detalles_precio (id_preciofk, id_detalleproductofk) VALUES
(3, 'BAR001'), (1, 'BAR003'), (2, 'BAR003'), (4, 'BAR004');

-- ============================================================
-- 11. INGREDIENTES
-- ============================================================
INSERT INTO ingredientes (cantidad, unidad_medida, id_producto_ingredientefk, id_producto_finalfk) VALUES
(200, 'Gramos', 2, 1),
(100, 'Gramos', 3, 1),
(50, 'Gramos', 2, 3),
(1, 'Unidad', 5, 1); -- Servilleta acompaña a hamburguesa

-- ============================================================
-- 13. PROVEEDORES (Combos de correo)
-- ============================================================
INSERT INTO proveedores (id, id_personafk, razon_social, ruc, correo, estado) VALUES
(1, 1234567, 'Distri A', 800123, 'a@a.com', true),
(2, 2345678, 'Frigo B', 800234, NULL, true),
(3, 3456789, 'Import C', 800345, NULL, false),
(4, 4567890, 'Lacteos D', 800456, 'd@d.com', true);

-- ============================================================
-- 14. CLIENTES (Combos ruc/razon_social)
-- ============================================================
INSERT INTO clientes (id, id_personafk, ruc, razon_social, persona_fisica) VALUES
(1, 1234567, 1234567, 'Juan Perez', 1),   -- Todo
(2, 2345678, NULL, NULL, 1),              -- Nada (Consumidor final)
(3, 3456789, 800999, 'Empresa S.A.', 0),  -- Persona Jurídica
(4, 4567890, 4567890, NULL, 1);           -- Solo RUC

-- ============================================================
-- 15. VENDEDORES (Combos comision y cod_num)
-- ============================================================
INSERT INTO vendedores (id, salario, comision, cod_num, estado, id_usuariofk) VALUES
(1, 2500000, 5.0, 'V01', true, 1),
(2, 2500000, NULL, 'V02', true, 2),
(3, 2000000, 2.5, NULL, false, 3),
(4, 3000000, NULL, NULL, true, 4);

-- ============================================================
-- 16. LOCALES (Combos direccion, telefono, coords)
-- ============================================================
INSERT INTO locales (id, nombre, direccion, cod_num, telefono, estado, latitud, longitud) VALUES
(1, 'Matriz', 'Centro', 'L01', '021123', true, -25.748, -56.435),
(2, 'Suc 2', NULL, NULL, NULL, true, NULL, NULL),
(3, 'Suc 3', 'Barrio', 'L03', NULL, false, -25.0, NULL),
(4, 'Suc 4', NULL, 'L04', '0981', true, NULL, -56.0);

-- ============================================================
-- 17. MESAS (Combos cliente fk y tiempo de ocupacion)
-- ============================================================
INSERT INTO mesas (id, nombre, estado, capacidad, id_localfk, id_clientefk, ocupado_desde) VALUES
(1, 'Mesa 1', 1, 4, 1, NULL, NULL),          -- Libre
(2, 'Mesa 2', 2, 2, 1, 1, '12:00:00'),       -- Ocupada con cliente
(3, 'Mesa 3', 3, 6, 1, 2, NULL),             -- Reservada
(4, 'Mesa 4', 2, 4, 1, NULL, '13:15:00');    -- Ocupada sin cliente asignado

-- ============================================================
-- 18. STOCKS (Combos lote y vencimiento)
-- ============================================================
INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, lote, fecha_vencimiento, id_detalleproductofk, id_localfk) VALUES
(1, 100, 20, 5, 'L123', '2026-12-31', 'BAR001', 1),
(2, 50, 0, 0, NULL, NULL, 'BAR002', 1),
(3, 200, 50, 10, 'L124', NULL, 'BAR003', 1),
(4, 0, 10, 0, NULL, '2026-08-01', 'BAR004', 1);

-- ============================================================
-- 19. CAJAS (Combos montos y cierres)
-- ============================================================
INSERT INTO cajas (id, fecha_cierre, monto_apertura, monto_cierre, id_usuariofk) VALUES
(1, '2026-07-13 23:59:59', 500000, 1500000, 1), -- Cerrada
(2, NULL, 500000, NULL, 1),                     -- Abierta
(3, NULL, 300000, NULL, 4),                     -- Abierta caja 2
(4, '2026-07-12 20:00:00', 100000, 100000, 3);  -- Cerrada sin ventas

-- ============================================================
-- 20. TIMBRADOS + SECUENCIAS_VENTA (para FK de ventas)
-- ============================================================
INSERT INTO timbrados (id, nro_timbrado, fin_vigencia) VALUES
(1, 'TIM-001', '2030-01-01 00:00:00-03'),
(2, 'TIM-002', '2030-01-01 00:00:00-03');

-- secuencias_venta: (id_localfk, id_vendedorfk, id_timbradofk, ultimo_nro)
INSERT INTO secuencias_venta (id, id_localfk, id_vendedorfk, id_timbradofk, ultimo_nro) VALUES
(1, 1, 1, 1, 0),
(2, 1, 4, 1, 0),
(3, 1, 1, 2, 0),
(4, 1, 4, 2, 0);

-- ============================================================
-- 21. VENTAS (Combos exhaustivos de clima, cuotas, entregas)
-- ============================================================
INSERT INTO ventas (id, fecha, total_cuotas, monto_entrega, tipo_credito, estado, cod_num, clima, temperatura, humedad, velocidad_viento, lluvia, precipitaciones, evento_festivo, cantidad_personas, ocupacion, id_clientefk, id_secuencias_ventafk) VALUES
(1, NOW(), NULL, 0, false, 1, 'V001', 1, 25, 60, 10.5, 0, 0, false, 2, '01:00:00', 1, 1), -- Todo lleno, contado
(2, NOW(), 3, 50000, true, 1, 'V002', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2, 1), -- Clima nulo, crédito c/entrega
(3, NOW(), 2, 0, true, 1, 'V003', 2, NULL, 80, NULL, 1.2, NULL, true, NULL, NULL, 3, 2), -- Clima parcial, crédito s/entrega
(4, NOW(), NULL, NULL, false, 0, NULL, NULL, 30, NULL, 5.0, NULL, 0, false, 4, '02:00:00', 4, 2); -- Anulada, todo parcial

-- ============================================================
-- 21. DETALLE VENTA (Combos de descuento)
-- ============================================================
INSERT INTO detalle_venta (id, cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(1, 2, 35000, NULL, 'BAR001', 1),
(2, 1, 15000, 1000, 'BAR003', 2),
(3, 5, 35000, 5000, 'BAR001', 3),
(4, 1, 10000, 0, 'BAR004', 4);

-- ============================================================
-- 22. CUOTAS VENTA (Combos de descuento/interes/foráneas)
-- ============================================================
INSERT INTO cuotas_venta (id, estado, monto, fecha, descuento, interes, id_ventafk, id_usuariofk) VALUES
(1, 1, 50000, '2026-08-14 10:00:00', NULL, NULL, 2, 1),
(2, 1, 50000, '2026-09-14 10:00:00', 2000, 0, 2, 1),
(3, 1, 100000, '2026-08-14 10:00:00', NULL, 10, 3, 4),
(4, 0, NULL, '2026-10-14 10:00:00', 0, NULL, NULL, NULL);

-- ============================================================
-- 23. PAGOS VENTA (Combos foráneas y tipos)
-- ============================================================
INSERT INTO pagos_venta (id, estado, tipo, monto, fecha, id_ventafk, id_cajafk) VALUES
(1, 1, 1, 70000, NOW(), 1, 2), -- Pago Venta Contado
(2, 1, 2, 50000, NOW(), 2, 2), -- Pago de Entrega
(3, 1, 3, 100000, NOW(), 3, 3),-- Pago de Cuota en otra caja
(4, 0, NULL, 15000, NOW(), NULL, NULL);

-- ============================================================
-- 24. COMPRAS (Combos cuotas, nro, entregas)
-- ============================================================
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(1, 'C-001', 1, NOW(), 1, 0, NULL, false, 1, 2), -- Contado
(2, NULL, 1, NOW(), 1, 20000, 2, true, 2, 2),    -- Crédito c/entrega sin Nro
(3, 'C-003', 1, NOW(), 1, 0, 3, true, 3, 3),     -- Crédito s/entrega
(4, NULL, 1, NOW(), 0, NULL, NULL, false, 4, 3); -- Anulado nulos

-- ============================================================
-- 25. DETALLE COMPRA
-- ============================================================
INSERT INTO detalle_compra (id_detalle_compra, cantidad, precio, id_comprafk, id_stockfk) VALUES
(1, 10, 30000, 1, 2),
(2, 50, 3500, 2, 3),
(3, 20, 30000, 3, 2),
(4, 5, 5000, 4, 4);

-- ============================================================
-- 26. EGRESOS (Combos descripcion y caja fk)
-- ============================================================
INSERT INTO egresos (id, estado, monto, descripcion, fecha, id_cajafk) VALUES
(1, 1, 150000, 'Pago ANDE', NOW(), 2),
(2, 1, 50000, NULL, NOW(), 2),
(3, 0, 100000, 'Egreso anulado', NOW(), 3),
(4, 1, 20000, 'Varios', NOW(), NULL);

-- ============================================================
-- 27. ORDENES (Combos exhaustivos FK opcionales)
-- ============================================================
INSERT INTO ordenes (id, estado, cantidad, observacion, id_mesafk, id_usuariofk, id_detalleproductofk, id_preciofk) VALUES
(1, 1, 2, 'Sin mayonesa', 2, 3, 'BAR001', 3), -- Todo lleno (Mesa)
(2, 2, 1, NULL, NULL, 3, 'BAR003', 1),        -- Sin mesa (Mostrador/Delivery)
(3, 3, 4, NULL, 4, NULL, 'BAR001', NULL),     -- Sin usuario ni precio
(4, 4, 1, 'Extra hielo', NULL, NULL, NULL, NULL);

-- ============================================================
-- 28. RESERVAS (Combos observacion, FK de mesas, usuarios y clientes)
-- ============================================================
INSERT INTO reservas (id, estado, cantidad_personas, observacion, fecha_reserva, id_mesafk, id_usuariofk, id_clientefk) VALUES
(1, 1, 4, 'Cena familiar', '2026-07-20 20:00:00', 3, 1, 1),  -- Todo lleno
(2, 1, 2, NULL, '2026-07-21 21:00:00', NULL, 4, 2),          -- Sin mesa asig
(3, 0, 6, 'Cumpleaños', '2026-07-22 19:00:00', 1, NULL, 3),  -- Sin usuario
(4, 1, 10, NULL, '2026-07-23 20:00:00', NULL, NULL, NULL);   -- Sin FKs

-- ============================================================
-- 29. CUOTAS COMPRA (Combos interes/descuentos)
-- ============================================================
INSERT INTO cuotas_compra (id, estado, monto, fecha, descuento, interes, id_comprafk, id_usuariofk) VALUES
(1, 1, 10000, '2026-08-14 00:00:00', NULL, NULL, 2, 1),
(2, 1, 10000, '2026-09-14 00:00:00', 1000, 0, 2, 1),
(3, 1, 15000, '2026-08-14 00:00:00', NULL, 5, 3, NULL),
(4, 1, NULL, '2026-10-14 00:00:00', 0, NULL, NULL, 4);

-- ============================================================
-- 30. PAGOS COMPRA
-- ============================================================
INSERT INTO pagos_compra (id, estado, monto, fecha, id_comprafk, id_cajafk) VALUES
(1, 1, 300000, NOW(), 1, 2),
(2, 1, 20000, NOW(), 2, 2),
(3, 1, 15000, NOW(), 3, 3),
(4, 0, NULL, NOW(), NULL, NULL);

-- ============================================================
-- 1. PRODUCTOS (Mayor variedad con combinaciones de reglas)
-- IDs inician en 100 para evitar conflictos con registros previos.
-- ============================================================
INSERT INTO productos (id, nombre, descripcion, estado, impuesto, pesable, perecedero, costeo, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES
(101, 'Lomito Árabe', 'Carne vacuna, salsa de ajo, lechuga', 1, 10, false, true, 18000, 'Unidad', false, true, 2, 3), -- Solo Comida
(102, 'Empanada Frita', 'Empanada tradicional', 1, 10, false, true, 2000, 'Unidad', false, true, 2, 3),          -- Solo Comida
(103, 'Tapa Cuadril', 'Corte premium', 1, 5, true, true, 45000, 'Kg', true, false, 3, 3),                        -- Solo Ingrediente
(104, 'Masa para Empanadas', 'Discos de masa', 1, 5, false, true, 3000, 'Paquete', true, false, 3, 3),           -- Solo Ingrediente
(105, 'Cerveza Pilsen', 'Cerveza rubia', 1, 10, false, false, 5000, 'Unidad', false, false, 1, 1),               -- Producto Normal (Ninguno)
(106, 'Queso Muzzarella', 'Queso en bloque', 1, 5, true, true, 35000, 'Kg', true, true, 3, 2);                   -- Ambos (Comida e Ingrediente)

-- ============================================================
-- 2. DETALLES PRODUCTO (Exactamente 3 por cada producto)
-- ============================================================
INSERT INTO detalles_producto (cod_barra, unidad_por_lote, color, tamanho, id_productofk) VALUES
-- Variaciones de Lomito (101)
('LOM-001', 1, 'Normal', 15, 101),
('LOM-002', 1, 'Doble', 25, 101),
('LOM-003', 1, 'Picante', 15, 101),

-- Variaciones de Empanada (102)
('EMP-001', 1, 'Carne', NULL, 102),
('EMP-002', 1, 'Pollo', NULL, 102),
('EMP-003', 1, 'Mandioca', NULL, 102),

-- Variaciones de Tapa Cuadril (103)
('CAR-001', 1, NULL, 1000, 103),  -- Pieza 1kg
('CAR-002', 5, NULL, 5000, 103),  -- Pieza 5kg
('CAR-003', 10, NULL, 10000, 103),-- Caja 10kg

-- Variaciones de Masa (104)
('MAS-001', 12, 'Blanca', NULL, 104), -- 12 unidades
('MAS-002', 24, 'Blanca', NULL, 104), -- 24 unidades
('MAS-003', 12, 'Horno', NULL, 104),  -- Para horno

-- Variaciones de Cerveza (105)
('CER-001', 1, 'Lata', 354, 105),
('CER-002', 1, 'Botella', 730, 105),
('CER-003', 6, 'Pack', 354, 105),

-- Variaciones de Queso (106)
('QUE-001', 1, 'Horma', 1000, 106),
('QUE-002', 1, 'Horma', 3000, 106),
('QUE-003', 1, 'Feteado', 200, 106);

-- ============================================================
-- 3. COMPRAS (10 Registros con variaciones de Crédito/Contado)
-- ============================================================
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(101, '001-001-00050', 1, NOW(), 1, 0, NULL, false, 1, 2),     -- Contado, con factura
(102, NULL, 1, NOW(), 1, 50000, 3, true, 2, 2),                -- Crédito con entrega, sin factura (interno)
(103, '001-002-00120', 1, NOW(), 1, 0, 2, true, 3, 2),         -- Crédito sin entrega
(104, NULL, 1, NOW(), 1, 0, NULL, false, 1, 3),                -- Contado, nulos
(105, 'F-9988', 1, NOW(), 1, 100000, 6, true, 2, 2),           -- Crédito a largo plazo
(106, '002-001-00005', 1, NOW(), 1, 0, NULL, false, 3, 3),
(107, NULL, 1, NOW(), 1, 25000, 2, true, 1, 2),
(108, '001-001-00051', 1, NOW(), 0, 0, NULL, false, 2, 2),     -- Compra anulada
(109, '003-001-00400', 1, NOW(), 1, 0, 4, true, 3, 3),
(110, NULL, 1, NOW(), 1, 0, NULL, false, 1, 2);

-- ============================================================
-- 4. STOCKS (Se generan los lotes provenientes de las compras)
-- ============================================================
INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, lote, fecha_vencimiento, id_detalleproductofk, id_localfk) VALUES
(101, 50, 0, 0, 'LT-A1', '2026-08-01', 'CAR-001', 1),   -- Stock para compra 101
(102, 100, 20, 0, 'LT-A2', '2026-12-31', 'CER-002', 1), -- Stock para compra 101
(103, 30, 0, 0, NULL, '2026-07-25', 'MAS-002', 1),      -- Stock para compra 102
(104, 15, 5, 0, 'QUESO-1', '2026-09-15', 'QUE-001', 1), -- Stock para compra 103
(105, 200, 50, 10, NULL, NULL, 'CER-001', 1),           -- Stock para compra 104
(106, 10, 0, 0, 'LT-B1', '2026-08-10', 'CAR-003', 1),   -- Stock para compra 105
(107, 40, 10, 0, NULL, '2026-08-05', 'EMP-001', 1),     -- Stock para compra 106 (Empanadas congeladas)
(108, 60, 0, 0, 'LT-C1', '2026-10-01', 'QUE-002', 1),   -- Stock para compra 107
(109, 0, 0, 0, NULL, NULL, 'MAS-001', 1),               -- Stock para compra 108 (Anulada)
(110, 120, 24, 0, 'PACK-01', '2027-01-01', 'CER-003', 1),-- Stock para compra 109
(111, 20, 0, 0, NULL, '2026-07-30', 'CAR-002', 1);      -- Stock para compra 110

-- ============================================================
-- 5. DETALLE COMPRA (Vincula la Compra con el Stock generado)
-- ============================================================
INSERT INTO detalle_compra (id_detalle_compra, cantidad, precio, id_comprafk, id_stockfk) VALUES
(101, 50, 40000, 101, 101),  -- Compra Tapa Cuadril
(102, 120, 6000, 101, 102),  -- Compra Cerveza Botella
(103, 30, 5000, 102, 103),   -- Compra Masa 24u
(104, 20, 32000, 103, 104),  -- Compra Queso Horma
(105, 250, 4000, 104, 105),  -- Compra Cerveza Lata
(106, 10, 380000, 105, 106), -- Compra Tapa Cuadril 10kg
(107, 50, 1500, 106, 107),   -- Compra Empanadas congeladas
(108, 60, 90000, 107, 108),  -- Compra Queso Horma 3kg
(109, 10, 2500, 108, 109),   -- Compra anulada
(110, 144, 20000, 109, 110), -- Compra Cerveza Pack
(111, 20, 190000, 110, 111); -- Compra Tapa Cuadril 5kg

-- ============================================================
-- 6. VENTAS (10 Registros con combinaciones de Ocupación, Clima y Personas)
-- ============================================================
INSERT INTO ventas (id, fecha, total_cuotas, monto_entrega, tipo_credito, estado, cod_num, clima, temperatura, humedad, velocidad_viento, lluvia, precipitaciones, evento_festivo, cantidad_personas, ocupacion, id_clientefk, id_secuencias_ventafk) VALUES
(101, NOW(), NULL, 0, false, 1, 'V101', 1, 28, 65, 10.0, 0, 0, false, 4, '01:30:00', 1, 1),
(102, NOW(), 2, 0, true, 1, 'V102', 3, 18, 90, 25.5, 15.2, 15.2, false, 2, '00:45:00', 2, 2),
(103, NOW(), NULL, NULL, false, 1, 'V103', NULL, 32, NULL, NULL, NULL, NULL, true, NULL, NULL, 3, 1),
(104, NOW(), 4, 20000, true, 1, 'V104', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 6, '02:15:00', 1, 4), 
(105, NOW(), NULL, 0, false, 1, 'V105', 2, 22, 70, 5.0, 0, 0, false, NULL, NULL, 4, 1),
(106, NOW(), 3, 0, true, 1, 'V106', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 8, '03:00:00', 2, 2),
(107, NOW(), NULL, 0, false, 1, 'V107', 1, 35, 50, 12.0, 0, 0, false, 1, '00:20:00', 3, 1),
(108, NOW(), NULL, 0, false, 0, 'V108', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 4),
(109, NOW(), 5, 50000, true, 1, 'V109', 4, 15, 95, 30.0, 20.0, 20.0, false, 10, '04:00:00', 2, 1),
(110, NOW(), NULL, 0, false, 1, 'V110', NULL, 26, 80, NULL, NULL, NULL, true, 3, '01:00:00', 4, 2);

-- ============================================================
-- 7. DETALLE VENTA (Combinaciones de comidas listas, ingredientes y normales)
-- ============================================================
INSERT INTO detalle_venta (id, cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
-- Venta 101 (Lomitos y Cervezas)
(101, 2, 22000, 0, 'LOM-002', 101),    -- Lomito Doble
(102, 2, 10000, NULL, 'CER-002', 101), -- Cerveza Ñoño
-- Venta 102 (Empanadas)
(103, 6, 3000, 2000, 'EMP-001', 102),  -- Empanada de Carne
(104, 2, 3000, 0, 'EMP-003', 102),     -- Empanada de Mandioca
-- Venta 103
(105, 1, 20000, NULL, 'LOM-003', 103), -- Lomito Picante
(106, 1, 6000, NULL, 'CER-001', 103),  -- Lata Cerveza
-- Venta 104
(107, 10, 3000, 5000, 'EMP-002', 104), -- Empanada de Pollo
(108, 2, 25000, 0, 'CER-003', 104),    -- Pack de Cervezas
-- Venta 105
(109, 1, 120000, NULL, 'CAR-002', 105),-- Cliente comprando Tapa Cuadril cruda (Ingrediente)
-- Venta 106
(110, 4, 20000, 0, 'LOM-001', 106),    -- Lomitos Normales
(111, 4, 6000, NULL, 'CER-001', 106),
-- Venta 107
(112, 1, 35000, 0, 'QUE-001', 107),    -- Cliente comprando Horma de Queso
-- Venta 108 (Anulada)
(113, 2, 22000, 0, 'LOM-002', 108),
-- Venta 109 (Mesa grande)
(114, 10, 20000, 15000, 'LOM-001', 109),
(115, 10, 10000, 5000, 'CER-002', 109),
-- Venta 110
(116, 3, 3000, 0, 'EMP-003', 110),
(117, 1, 20000, NULL, 'LOM-003', 110);

-- Reinicio de secuencias para todas las tablas con IDENTITY
SELECT setval(pg_get_serial_sequence('roles', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM roles;
SELECT setval(pg_get_serial_sequence('permisos', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM permisos;
SELECT setval(pg_get_serial_sequence('permisos_roles', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM permisos_roles;
SELECT setval(pg_get_serial_sequence('marcas', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM marcas;
SELECT setval(pg_get_serial_sequence('categorias', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM categorias;
SELECT setval(pg_get_serial_sequence('precios', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM precios;
SELECT setval(pg_get_serial_sequence('productos', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM productos;
SELECT setval(pg_get_serial_sequence('detalles_precio', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM detalles_precio;
SELECT setval(pg_get_serial_sequence('ingredientes', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM ingredientes;
SELECT setval(pg_get_serial_sequence('usuarios', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM usuarios;
SELECT setval(pg_get_serial_sequence('proveedores', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM proveedores;
SELECT setval(pg_get_serial_sequence('clientes', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM clientes;
SELECT setval(pg_get_serial_sequence('vendedores', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM vendedores;
SELECT setval(pg_get_serial_sequence('locales', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM locales;
SELECT setval(pg_get_serial_sequence('mesas', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM mesas;
SELECT setval(pg_get_serial_sequence('stocks', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM stocks;
SELECT setval(pg_get_serial_sequence('cajas', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM cajas;
SELECT setval(pg_get_serial_sequence('timbrados', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM timbrados;
SELECT setval(pg_get_serial_sequence('secuencias_venta', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM secuencias_venta;
SELECT setval(pg_get_serial_sequence('ventas', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM ventas;
SELECT setval(pg_get_serial_sequence('detalle_venta', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM detalle_venta;
SELECT setval(pg_get_serial_sequence('cuotas_venta', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM cuotas_venta;
SELECT setval(pg_get_serial_sequence('pagos_venta', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM pagos_venta;
SELECT setval(pg_get_serial_sequence('compras', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM compras;

-- Cuidado aquí: La PK se llama id_detalle_compra
SELECT setval(pg_get_serial_sequence('detalle_compra', 'id_detalle_compra'), COALESCE(MAX(id_detalle_compra), 0) + 1, false) FROM detalle_compra;

SELECT setval(pg_get_serial_sequence('egresos', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM egresos;
SELECT setval(pg_get_serial_sequence('ordenes', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM ordenes;
SELECT setval(pg_get_serial_sequence('reservas', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM reservas;
SELECT setval(pg_get_serial_sequence('cuotas_compra', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM cuotas_compra;
SELECT setval(pg_get_serial_sequence('pagos_compra', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM pagos_compra;
SELECT setval(pg_get_serial_sequence('timbrados', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM timbrados;
SELECT setval(pg_get_serial_sequence('secuencias_venta', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM secuencias_venta;
