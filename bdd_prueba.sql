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
-- 3. LOCALES Y MESAS
-- ============================================================
INSERT INTO locales (id, nombre, direccion, cod_num, telefono, estado, latitud, longitud) VALUES
(1, 'Local Principal', 'Bvr. Yegros', 'L01', '021000111', true, -25.78, -56.43);

INSERT INTO mesas (id, nombre, estado, capacidad, id_localfk) VALUES
(1, 'Mesa 1', 1, 4, 1), (2, 'Mesa 2', 0, 2, 1);

-- ============================================================
-- 4. CLIENTES Y PROVEEDORES
-- ============================================================
INSERT INTO clientes (id, id_personafk, ruc, razon_social, persona_fisica) VALUES
(1, 3000001, null, 'Juan Pérez 1', 1), (2, 3000002, null, 'María López 1', 1), (3, 3000003, null, 'Carlos Gómez 1', 1),
(4, 3000001, 30000018, 'Juan Pérez 2', 1), (5, 3000002, 30000029, 'María López 2', 1), (6, 3000003, 30000030, 'Carlos Gómez 2', 1),
(7, 3000004, null, 'Constructora XYZ 1', 0), (8, 3000005, null, 'Empresa Sin RUC 1', 0), (9, 3000004, null, 'Constructora XYZ 2', 0),
(10, 3000004, 80012345, 'Constructora XYZ 3', 0), (11, 3000005, 80099999, 'Empresa Local S.A.', 0), (12, 3000004, 80011111, 'Constructora XYZ 4', 0);

INSERT INTO proveedores (id, id_personafk, razon_social, ruc, correo, estado) VALUES
(1, 2000001, 'Distri Guairá A', 80000011, null, true), (2, 2000002, 'Frigorífico A', 80000022, null, true), (3, 2000003, 'Bebidas A', 80000033, null, true),
(4, 2000001, 'Distri Guairá B', 80000044, 'ventas1@guaira.com', true), (5, 2000002, 'Frigorífico B', 80000055, 'carne1@frigo.com', true), (6, 2000003, 'Bebidas B', 80000066, 'pedidos@bebidas.com', true);

INSERT INTO vendedores (id, salario, comision, cod_num, estado, id_usuariofk) VALUES
(1, 3000000, 3.5, 'V01', true, 4), (2, 3000000, 3.5, 'V02', true, 5);

-- ============================================================
-- 5. PRODUCTOS, PRECIOS Y STOCK
-- ============================================================
INSERT INTO categorias (id, nombre, estado) VALUES (1, 'General', 1);
INSERT INTO marcas (id, nombre, estado) VALUES (1, 'Genérica', 1);

INSERT INTO productos (id, nombre, estado, impuesto, pesable, perecedero, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES
(1, 'Gaseosa Lata 1', 1, 10, false, false, 'Unidad', false, false, 1, 1), (2, 'Gaseosa Lata 2', 1, 10, false, false, 'Unidad', false, false, 1, 1), (3, 'Gaseosa Lata 3', 1, 10, false, false, 'Unidad', false, false, 1, 1),
(4, 'Clavos x Kilo 1', 1, 10, true, false, 'Kg', false, false, 1, 1), (5, 'Clavos x Kilo 2', 1, 10, true, false, 'Kg', false, false, 1, 1), (6, 'Clavos x Kilo 3', 1, 10, true, false, 'Kg', false, false, 1, 1),
(7, 'Empanada 1', 1, 5, false, true, 'Unidad', false, true, 1, 1), (8, 'Empanada 2', 1, 5, false, true, 'Unidad', false, true, 1, 1), (9, 'Empanada 3', 1, 5, false, true, 'Unidad', false, true, 1, 1),
(10, 'Colorante 1', 1, 5, false, false, 'Unidad', true, false, 1, 1), (11, 'Colorante 2', 1, 5, false, false, 'Unidad', true, false, 1, 1), (12, 'Colorante 3', 1, 5, false, false, 'Unidad', true, false, 1, 1),
(13, 'Asado Crudo 1', 1, 5, true, true, 'Kg', false, true, 1, 1), (14, 'Asado Crudo 2', 1, 5, true, true, 'Kg', false, true, 1, 1), (15, 'Asado Crudo 3', 1, 5, true, true, 'Kg', false, true, 1, 1),
(16, 'Sal Gruesa 1', 1, 5, true, false, 'Kg', true, false, 1, 1), (17, 'Sal Gruesa 2', 1, 5, true, false, 'Kg', true, false, 1, 1), (18, 'Sal Gruesa 3', 1, 5, true, false, 'Kg', true, false, 1, 1),
(19, 'Leche Sachet 1', 1, 5, false, true, 'Unidad', true, false, 1, 1), (20, 'Leche Sachet 2', 1, 5, false, true, 'Unidad', true, false, 1, 1), (21, 'Leche Sachet 3', 1, 5, false, true, 'Unidad', true, false, 1, 1),
(22, 'Queso Paraguay 1', 1, 5, true, true, 'Kg', true, false, 1, 1), (23, 'Queso Paraguay 2', 1, 5, true, true, 'Kg', true, false, 1, 1), (24, 'Queso Paraguay 3', 1, 5, true, true, 'Kg', true, false, 1, 1);

INSERT INTO detalles_producto (cod_barra, unidad_por_lote, id_productofk) VALUES
('P001',1,1), ('P002',1,2), ('P003',1,3), ('P004',1,4), ('P005',1,5), ('P006',1,6),
('P007',1,7), ('P008',1,8), ('P009',1,9), ('P010',1,10), ('P011',1,11), ('P012',1,12),
('P013',1,13), ('P014',1,14), ('P015',1,15), ('P016',1,16), ('P017',1,17), ('P018',1,18),
('P019',1,19), ('P020',1,20), ('P021',1,21), ('P022',1,22), ('P023',1,23), ('P024',1,24);

INSERT INTO precios (id, monto, valido_desde) VALUES 
(1,5000,NOW()),(2,5000,NOW()),(3,5000,NOW()),(4,10000,NOW()),(5,10000,NOW()),(6,10000,NOW()),
(7,15000,NOW()),(8,15000,NOW()),(9,15000,NOW()),(10,20000,NOW()),(11,20000,NOW()),(12,20000,NOW()),
(13,25000,NOW()),(14,25000,NOW()),(15,25000,NOW()),(16,30000,NOW()),(17,30000,NOW()),(18,30000,NOW()),
(19,35000,NOW()),(20,35000,NOW()),(21,35000,NOW()),(22,40000,NOW()),(23,40000,NOW()),(24,40000,NOW());

INSERT INTO detalles_precio (id_preciofk, id_detalleproductofk) VALUES
(1,'P001'),(2,'P002'),(3,'P003'),(4,'P004'),(5,'P005'),(6,'P006'),(7,'P007'),(8,'P008'),
(9,'P009'),(10,'P010'),(11,'P011'),(12,'P012'),(13,'P013'),(14,'P014'),(15,'P015'),(16,'P016'),
(17,'P017'),(18,'P018'),(19,'P019'),(20,'P020'),(21,'P021'),(22,'P022'),(23,'P023'),(24,'P024');

-- Es crucial tener registros en 'stocks' para poder vincularlos con el detalle de las compras
INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, id_detalleproductofk, id_localfk) VALUES
(1, 100, 20, 0, 'P001', 1), (2, 100, 20, 0, 'P002', 1), (3, 100, 20, 0, 'P003', 1),
(4, 50, 10, 0, 'P004', 1),  (5, 50, 10, 0, 'P005', 1),  (6, 50, 10, 0, 'P006', 1);

-- ============================================================
-- 6. CAJAS
-- ============================================================
INSERT INTO cajas (id, monto_apertura, id_usuariofk) VALUES (1, 100000, 2);

-- ============================================================
-- 7. VENTAS (3 Días x 4 Permutaciones x 3 registros = 36 Ventas)
-- Permutaciones: tipo_credito (A), evento_festivo (B)
-- ============================================================
-- ============================================================
-- 7. VENTAS (3 Días x 4 Permutaciones x 3 registros = 36 Ventas)
-- Permutaciones basadas en: tipo_credito (A) y evento_festivo (B)
-- Incluye variables climáticas extendidas y tiempos de ocupación.
-- ============================================================

-- --- DÍA 1: HOY (NOW()) ---
-- Permutación 1: Contado, Sin Evento (A=false, B=false) -> cuotas=0, entrega=0
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, cod_num, clima, temperatura, humedad, velocidad_viento, lluvia, precipitaciones, probabilidad_precipitaciones, evento_festivo, ocupacion, id_clientefk, id_localfk, id_vendedorfk) VALUES
(1, 'V-001', NOW(), 0, 0, false, 1, 'FAC001', 0, 35, 60, 12.5, 0.0, 0.0, 5.0, false, '00:45:00', 1, 1, 1),
(2, 'V-002', NOW(), 0, 0, false, 1, 'FAC002', 0, 34, 62, 10.2, 0.0, 0.0, 5.0, false, '01:15:00', 2, 1, 2),
(3, 'V-003', NOW(), 0, 0, false, 1, 'FAC003', 0, 35, 59, 14.0, 0.0, 0.0, 10.0, false, '00:30:00', 3, 1, 1),

-- Permutación 2: Crédito, Sin Evento (A=true, B=false) -> cuotas>0, entrega variable
(4, 'V-004', NOW(), 3, 50000, true, 1, 'FAC004', 0, 32, 65, 8.5, 0.0, 0.0, 15.0, false, '01:40:00', 4, 1, 2),
(5, 'V-005', NOW(), 2, 0, true, 1, 'FAC005', 0, 31, 66, 9.0, 0.0, 0.0, 15.0, false, '02:00:00', 5, 1, 1),
(6, 'V-006', NOW(), 4, 100000, true, 1, 'FAC006', 0, 32, 64, 11.1, 0.0, 0.0, 20.0, false, '01:10:00', 6, 1, 2),

-- Permutación 3: Contado, Con Evento (A=false, B=true) -> Alto movimiento, ocupación más larga
(7, 'V-007', NOW(), 0, 0, false, 1, 'FAC007', 1, 28, 70, 18.5, 0.0, 0.0, 40.0, true, '02:15:00', 7, 1, 1),
(8, 'V-008', NOW(), 0, 0, false, 1, 'FAC008', 1, 27, 72, 20.0, 0.5, 0.5, 50.0, true, '01:50:00', 8, 1, 2),
(9, 'V-009', NOW(), 0, 0, false, 1, 'FAC009', 1, 28, 71, 16.2, 0.0, 0.0, 45.0, true, '02:30:00', 9, 1, 1),

-- Permutación 4: Crédito, Con Evento (A=true, B=true)
(10, 'V-010', NOW(), 3, 150000, true, 1, 'FAC010', 1, 26, 75, 22.0, 1.2, 1.2, 70.0, true, '03:00:00', 10, 1, 2),
(11, 'V-011', NOW(), 5, 200000, true, 1, 'FAC011', 1, 25, 78, 25.4, 2.0, 2.0, 85.0, true, '01:35:00', 11, 1, 1),
(12, 'V-012', NOW(), 2, 50000, true, 1, 'FAC012', 1, 26, 76, 21.0, 1.5, 1.5, 80.0, true, '02:05:00', 12, 1, 2),


-- --- DÍA 2: AYER (NOW() - INTERVAL '1 day') ---
-- Permutación 1: Contado, Sin Evento (A=false, B=false)
(13, 'V-013', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC013', 2, 22, 80, 15.0, 4.5, 4.5, 90.0, false, '00:50:00', 1, 1, 2),
(14, 'V-014', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC014', 2, 21, 82, 14.2, 5.0, 5.0, 95.0, false, '01:05:00', 2, 1, 1),
(15, 'V-015', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC015', 2, 22, 81, 16.0, 3.8, 3.8, 85.0, false, '00:55:00', 3, 1, 2),

-- Permutación 2: Crédito, Sin Evento (A=true, B=false)
(16, 'V-016', NOW() - INTERVAL '1 day', 2, 30000, true, 1, 'FAC016', 2, 20, 85, 12.0, 2.1, 2.1, 60.0, false, '01:20:00', 4, 1, 1),
(17, 'V-017', NOW() - INTERVAL '1 day', 3, 0, true, 1, 'FAC017', 2, 19, 88, 10.5, 1.0, 1.0, 40.0, false, '01:45:00', 5, 1, 2),
(18, 'V-018', NOW() - INTERVAL '1 day', 4, 80000, true, 1, 'FAC018', 2, 20, 86, 11.8, 1.5, 1.5, 50.0, false, '01:15:00', 6, 1, 1),

-- Permutación 3: Contado, Con Evento (A=false, B=true)
(19, 'V-019', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC019', 3, 18, 90, 28.0, 12.0, 12.0, 100.0, true, '02:40:00', 7, 1, 2),
(20, 'V-020', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC020', 3, 17, 92, 30.5, 15.0, 15.0, 100.0, true, '01:55:00', 8, 1, 1),
(21, 'V-021', NOW() - INTERVAL '1 day', 0, 0, false, 1, 'FAC021', 3, 18, 91, 26.2, 10.5, 10.5, 95.0, true, '02:10:00', 9, 1, 2),

-- Permutación 4: Crédito, Con Evento (A=true, B=true)
(22, 'V-022', NOW() - INTERVAL '1 day', 3, 40000, true, 1, 'FAC022', 3, 16, 95, 32.0, 18.0, 18.0, 100.0, true, '01:50:00', 10, 1, 1),
(23, 'V-023', NOW() - INTERVAL '1 day', 6, 0, true, 1, 'FAC023', 3, 15, 96, 35.0, 22.5, 22.5, 100.0, true, '03:10:00', 11, 1, 2),
(24, 'V-024', NOW() - INTERVAL '1 day', 2, 150000, true, 1, 'FAC024', 3, 16, 94, 29.0, 14.0, 14.0, 100.0, true, '02:25:00', 12, 1, 1),


-- --- DÍA 3: ANTEAYER (NOW() - INTERVAL '2 days') ---
-- Permutación 1: Contado, Sin Evento (A=false, B=false)
(25, 'V-025', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC025', 0, 30, 50, 8.0, 0.0, 0.0, 0.0, false, '00:40:00', 1, 1, 1),
(26, 'V-026', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC026', 0, 29, 52, 7.5, 0.0, 0.0, 0.0, false, '01:00:00', 2, 1, 2),
(27, 'V-027', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC027', 0, 30, 51, 9.2, 0.0, 0.0, 0.0, false, '00:50:00', 3, 1, 1),

-- Permutación 2: Crédito, Sin Evento (A=true, B=false)
(28, 'V-028', NOW() - INTERVAL '2 days', 3, 60000, true, 1, 'FAC028', 0, 28, 55, 6.0, 0.0, 0.0, 0.0, false, '01:15:00', 4, 1, 2),
(29, 'V-029', NOW() - INTERVAL '2 days', 2, 20000, true, 1, 'FAC029', 0, 27, 58, 5.4, 0.0, 0.0, 0.0, false, '01:30:00', 5, 1, 1),
(30, 'V-030', NOW() - INTERVAL '2 days', 4, 0, true, 1, 'FAC030', 0, 28, 56, 7.1, 0.0, 0.0, 5.0, false, '01:20:00', 6, 1, 2),

-- Permutación 3: Contado, Con Evento (A=false, B=true)
(31, 'V-031', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC031', 1, 25, 60, 11.0, 0.0, 0.0, 10.0, true, '02:00:00', 7, 1, 1),
(32, 'V-032', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC032', 1, 24, 62, 13.4, 0.0, 0.0, 15.0, true, '02:20:00', 8, 1, 2),
(33, 'V-033', NOW() - INTERVAL '2 days', 0, 0, false, 1, 'FAC033', 1, 25, 61, 10.0, 0.0, 0.0, 10.0, true, '01:45:00', 9, 1, 1),

-- Permutación 4: Crédito, Con Evento (A=true, B=true)
(34, 'V-034', NOW() - INTERVAL '2 days', 3, 50000, true, 1, 'FAC034', 1, 23, 65, 14.0, 0.0, 0.0, 20.0, true, '02:30:00', 10, 1, 2),
(35, 'V-035', NOW() - INTERVAL '2 days', 2, 100000, true, 1, 'FAC035', 1, 22, 68, 15.5, 0.2, 0.2, 30.0, true, '01:55:00', 11, 1, 1),
(36, 'V-036', NOW() - INTERVAL '2 days', 4, 40000, true, 1, 'FAC036', 1, 23, 66, 12.1, 0.0, 0.0, 25.0, true, '02:10:00', 12, 1, 2);


-- ============================================================
-- DETALLES DE VENTA (Vínculo correlativo estricto 1 a 1 con ventas)
-- ============================================================
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
-- Detalles Día 1 (Ventas 1 al 12)
(1, 5000, 0, 'P001', 1),   (2, 5000, 0, 'P002', 2),   (1, 5000, 0, 'P003', 3),
(1, 10000, 0, 'P004', 4),  (3, 10000, 0, 'P005', 5),  (1, 10000, 0, 'P006', 6),
(4, 15000, 0, 'P007', 7),  (2, 15000, 0, 'P008', 8),  (5, 15000, 0, 'P009', 9),
(2, 20000, 10, 'P010', 10),(1, 20000, 0, 'P011', 11), (3, 20000, 0, 'P012', 12),

-- Detalles Día 2 (Ventas 13 al 24)
(2, 5000, 0, 'P001', 13),  (1, 5000, 0, 'P002', 14),  (3, 5000, 0, 'P003', 15),
(1, 10000, 0, 'P004', 16), (2, 10000, 0, 'P005', 17), (1, 10000, 0, 'P006', 18),
(2, 15000, 0, 'P007', 19), (4, 15000, 0, 'P008', 20), (2, 15000, 0, 'P009', 21),
(1, 20000, 0, 'P010', 22), (5, 20000, 15, 'P011', 23),(2, 20000, 0, 'P012', 24),

-- Detalles Día 3 (Ventas 25 al 36)
(3, 5000, 0, 'P001', 25),  (2, 5000, 0, 'P002', 26),  (1, 5000, 0, 'P003', 27),
(2, 10000, 0, 'P004', 28), (1, 10000, 0, 'P005', 29), (3, 10000, 0, 'P006', 30),
(3, 15000, 0, 'P007', 31), (1, 15000, 0, 'P008', 32), (2, 15000, 0, 'P009', 33),
(2, 20000, 0, 'P010', 34), (2, 20000, 0, 'P011', 35), (4, 20000, 5, 'P012', 36);

-- ============================================================
-- 8. COMPRAS (3 Días x 2 Permutaciones x 3 registros = 18 Compras)
-- Permutaciones: tipo_credito (True / False)
-- ============================================================
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
-- --- DÍA 1: HOY ---
-- Contado
(1, 'C-001', 1, NOW(), 1, 0, 0, false, 1, 1),
(2, 'C-002', 1, NOW(), 1, 0, 0, false, 2, 1),
(3, 'C-003', 1, NOW(), 1, 0, 0, false, 3, 1),
-- Crédito
(4, 'C-004', 1, NOW(), 1, 50000, 3, true, 4, 1),
(5, 'C-005', 1, NOW(), 1, 60000, 2, true, 5, 1),
(6, 'C-006', 1, NOW(), 1, 40000, 4, true, 6, 1),

-- --- DÍA 2: AYER ---
-- Contado
(7, 'C-007', 1, NOW() - INTERVAL '1 day', 1, 0, 0, false, 1, 1),
(8, 'C-008', 1, NOW() - INTERVAL '1 day', 1, 0, 0, false, 2, 1),
(9, 'C-009', 1, NOW() - INTERVAL '1 day', 1, 0, 0, false, 3, 1),
-- Crédito
(10, 'C-010', 1, NOW() - INTERVAL '1 day', 1, 30000, 3, true, 4, 1),
(11, 'C-011', 1, NOW() - INTERVAL '1 day', 1, 20000, 2, true, 5, 1),
(12, 'C-012', 1, NOW() - INTERVAL '1 day', 1, 50000, 4, true, 6, 1),

-- --- DÍA 3: ANTEAYER ---
-- Contado
(13, 'C-013', 1, NOW() - INTERVAL '2 days', 1, 0, 0, false, 1, 1),
(14, 'C-014', 1, NOW() - INTERVAL '2 days', 1, 0, 0, false, 2, 1),
(15, 'C-015', 1, NOW() - INTERVAL '2 days', 1, 0, 0, false, 3, 1),
-- Crédito
(16, 'C-016', 1, NOW() - INTERVAL '2 days', 1, 100000, 5, true, 4, 1),
(17, 'C-017', 1, NOW() - INTERVAL '2 days', 1, 0, 3, true, 5, 1),
(18, 'C-018', 1, NOW() - INTERVAL '2 days', 1, 25000, 2, true, 6, 1);

-- Detalles de Compra correspondientes (Asociados a stocks id 1 al 6)
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES
(10, 4500, 1, 1), (10, 4500, 2, 2), (10, 4500, 3, 3), (5, 9000, 4, 4), (5, 9000, 5, 5), (5, 9000, 6, 6),
(10, 4500, 7, 1), (10, 4500, 8, 2), (10, 4500, 9, 3), (5, 9000, 10, 4), (5, 9000, 11, 5), (5, 9000, 6, 6),
(10, 4500, 13, 1), (10, 4500, 14, 2), (10, 4500, 15, 3), (5, 9000, 16, 4), (5, 9000, 17, 5), (5, 9000, 6, 6);


-- ============================================================
-- 9. EGRESOS (3 Días x 3 registros = 9 Egresos variados)
-- ============================================================
INSERT INTO egresos (estado, monto, descripcion, fecha, id_cajafk) VALUES
-- Hoy
(1, 150000, 'Pago de agua (ESSAP)', NOW(), 1),
(1, 45000, 'Compra de insumos de limpieza urgentes', NOW(), 1),
(1, 30000, 'Viático entrega de pedidos corporativos', NOW(), 1),
-- Ayer
(1, 450000, 'Pago de energía eléctrica (ANDE)', NOW() - INTERVAL '1 day', 1),
(1, 80000, 'Reparación menor cerradura puerta principal', NOW() - INTERVAL '1 day', 1),
(1, 25000, 'Hielo para conservación de bebidas', NOW() - INTERVAL '1 day', 1),
-- Anteayer
(1, 120000, 'Servicio técnico mantenimiento preventivo POS', NOW() - INTERVAL '2 days', 1),
(1, 35000, 'Compra de rollos de papel térmico para facturas', NOW() - INTERVAL '2 days', 1),
(1, 60000, 'Combustible para moto de delivery', NOW() - INTERVAL '2 days', 1);


-- ============================================================
-- 10. RESERVAS (Base Intacta)
-- ============================================================
INSERT INTO reservas (estado, cantidad_personas, fecha_reserva, observacion, id_clientefk, id_mesafk, id_usuariofk) VALUES
(1, 2, NOW() + INTERVAL '1 day', null, null, 1, 1),
(1, 4, NOW() + INTERVAL '2 days', null, null, 1, 1),
(1, 2, NOW() + INTERVAL '3 days', null, null, 1, 1),
(1, 4, NOW() + INTERVAL '1 day', 'Cerca de la ventana', null, 1, 1),
(1, 6, NOW() + INTERVAL '2 days', 'Traer sillita', null, 1, 1),
(1, 2, NOW() + INTERVAL '3 days', 'Alergia al maní', null, 1, 1),
(1, 2, NOW() + INTERVAL '1 day', null, 1, 1, 1),
(1, 4, NOW() + INTERVAL '2 days', null, 2, 1, 1),
(1, 2, NOW() + INTERVAL '3 days', null, 3, 1, 1),
(1, 8, NOW() + INTERVAL '1 day', 'Festejo de cumpleaños', 4, 1, 1),
(1, 10, NOW() + INTERVAL '2 days', 'Reunión de trabajo', 5, 1, 1),
(1, 4, NOW() + INTERVAL '3 days', 'Mesa tranquila', 6, 1, 1);