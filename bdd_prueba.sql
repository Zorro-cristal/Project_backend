PRAGMA foreign_keys = OFF;

-- ============================================================
-- 0. LIMPIEZA DE TABLAS (Idempotente)
-- ============================================================
DELETE FROM pagos_venta;
DELETE FROM cuotas_venta;
DELETE FROM detalle_venta;
DELETE FROM ventas;
DELETE FROM secuencias_venta;
DELETE FROM timbrados;
DELETE FROM pagos_compra;
DELETE FROM cuotas_compra;
DELETE FROM detalle_compra;
DELETE FROM compras;
DELETE FROM ordenes;
DELETE FROM reservas;
DELETE FROM mesas;
DELETE FROM cajas;
DELETE FROM stocks;
DELETE FROM detalles_precio;
DELETE FROM precios;
DELETE FROM detalles_producto;
DELETE FROM productos;
DELETE FROM categorias;
DELETE FROM proveedores;

DELETE FROM clientes WHERE id > 1;
DELETE FROM locales WHERE id > 1;
DELETE FROM marcas WHERE id > 1;
DELETE FROM personas WHERE cedula NOT IN (1, 4360067);

-- ============================================================
-- 1. LOCALES, CAJA Y MESAS
-- ============================================================
UPDATE locales SET cod_num = '001', latitud = -25.7500, longitud = -56.4333 WHERE id = 1;

INSERT INTO locales (id, nombre, cod_num, latitud, longitud) VALUES
(2, 'Sucursal Norte', '002', -25.7500, -56.4333);

INSERT INTO cajas (id, fecha_creado, monto_apertura, monto_cierre, id_usuariofk) VALUES 
(1, CURRENT_TIMESTAMP, 500000.00, NULL, 1);

-- Nota: Recordar que el trigger trg_crear_mesa_delivery ya crea la mesa 1 automáticamente al insertar locales[cite: 2], 
-- asumiendo que borramos y recreamos mesas, insertamos las físicas:
INSERT INTO mesas (id, nombre, estado, capacidad, id_localfk) VALUES
(1, 'Mesa 1', 1, 4, 1), (2, 'Mesa 2', 1, 2, 1), (3, 'Mesa 3', 1, 6, 1), (4, 'Mesa 4', 1, 4, 1);

-- ============================================================
-- 2. PERSONAS, CLIENTES Y PROVEEDORES
-- ============================================================
INSERT INTO personas (cedula, nombres, apellidos, telefono, direccion, nacionalidad) VALUES 
(2000002, 'Maria', 'Gomez', NULL, 'Barrio Centro', 'PRY'),
(2000003, 'Carlos', 'Lopez', '971654321', NULL, 'PRY'),
(2000004, 'Ana', 'Martinez', NULL, NULL, 'ARG'),
(3000001, 'Distribuidora', 'Sur', '982111222', 'Ruta 8 km 2', 'PRY'),
(3000002, 'Carnes', 'Premium', NULL, 'Mercado Central', 'PRY'),
(3000003, 'Bebidas', 'S.A.', '973333444', NULL, 'PRY'),
(3000004, 'Empaques', 'Global', NULL, NULL, 'PRY');

INSERT INTO clientes (id, id_personafk, ruc, razon_social, persona_fisica) VALUES
(2, 2000002, 0, NULL, 1),                
(3, 2000003, NULL, 'Carlos Lopez', 1),   
(4, 2000004, 7, 'Ana Martinez', 1);      

INSERT INTO proveedores (id, id_personafk, razon_social, ruc, correo, estado) VALUES
(1, 3000001, 'Distribuidora Sur S.A.', 5, 'ventas@dsur.com.py', 1),
(2, 3000002, 'Carnes Premium', 8, NULL, 1),
(3, 3000003, 'Bebidas S.A.', 1, 'contacto@bebidas.com', 1),
(4, 3000004, 'Empaques Global', 4, NULL, 1);

-- ============================================================
-- 3. PRODUCTOS -> VARIANTES (HEX PK) -> PRECIOS
-- ============================================================
INSERT INTO categorias (id, nombre, estado) VALUES 
(1, 'Comidas Rápidas', 1), (2, 'Bebidas', 1);

INSERT INTO marcas (id, nombre, estado) VALUES 
(2, 'Coca-Cola', 1), (3, 'Casero', 1);

-- PRODUCTOS MAESTROS
INSERT INTO productos (id, nombre, estado, impuesto, pesable, perecedero, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES 
(1, 'Coca cola', 1, 10, 0, 0, 'L', 0, 0, 2, 2),
(2, 'Fanta', 1, 10, 0, 0, 'L', 0, 0, 2, 2),
(3, 'Hamburguesa', 1, 10, 0, 1, 'UN', 0, 1, 1, 3), 
(4, 'Papas fritas', 1, 10, 0, 1, 'UN', 0, 1, 1, 3);

-- DETALLES DE PRODUCTO (LLAVE PRIMARIA HEXADECIMAL cod_barra)
INSERT INTO detalles_producto (cod_barra, unidad_por_lote, color, tamanho, id_productofk) VALUES 
('1000000A', 1, 'Tradicional', 1, 1),       -- Coca Cola 1L (ID 1)
('1000000B', 1, 'Tradicional', 500, 1),     -- Coca Cola 500ml (ID 1)
('1000000C', 1, 'Guaraná', 500, 2),         -- Fanta 500ml Guaraná (ID 2)
('1000000D', 1, 'Normal', 1, 3),            -- Hamburguesa 1 u (ID 3)
('1000000E', 1, 'Mitad', 0, 3),             -- Hamburguesa 0.5 u (ID 3)
('1000000F', 1, 'Normal', 1, 4);            -- Papas Fritas 1 u (ID 4)

-- PRECIOS
INSERT INTO precios (id, monto, valido_desde) VALUES 
(1, 10000.00, '2026-01-01'), -- Para Coca 1L
(2, 7000.00, '2026-01-01'),  -- Para Coca/Fanta 500ml
(3, 20000.00, '2026-01-01'), -- Para Hamb 1u / Papas 1u
(4, 12000.00, '2026-01-01'); -- Para Hamb 0.5u

-- VINCULO PRECIO -> VARIANTE HEX
INSERT INTO detalles_precio (id_preciofk, id_detalleproductofk) VALUES 
(1, '1000000A'), -- Coca 1L -> 10,000
(2, '1000000B'), -- Coca 500ml -> 7,000
(2, '1000000C'), -- Fanta 500ml Guarana -> 7,000
(3, '1000000D'), -- Hamb 1u -> 20,000
(4, '1000000E'), -- Hamb 0.5u -> 12,000
(3, '1000000F'); -- Papas 1u -> 20,000

-- STOCKS DE VARIANTE HEX (id incremental interno autogenerado)
INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, id_detalleproductofk, id_localfk) VALUES 
(1, 50, 20, 0, '1000000A', 1), 
(2, 50, 20, 0, '1000000B', 1), 
(3, 50, 20, 0, '1000000C', 1),
(4, 50, 20, 0, '1000000D', 1), 
(5, 50, 20, 0, '1000000E', 1), 
(6, 50, 20, 0, '1000000F', 1);

-- ============================================================
-- 4. COMPRAS (16 Casos - Usando id_stockfk como manda la tabla detalle_compra)
-- ============================================================
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES 
-- 4x Contado
(1, '001-001-001', 1, CURRENT_TIMESTAMP, 1, 150000.0, 0, 0, 1, 1),
(2, '001-001-002', 1, CURRENT_TIMESTAMP, 1, 70000.0,  0, 0, 2, 1),
(3, '001-001-003', 1, CURRENT_TIMESTAMP, 1, 50000.0,  0, 0, 3, 1),
(4, '001-001-004', 1, CURRENT_TIMESTAMP, 1, 60000.0,  0, 0, 4, 1),
-- 4x Crédito Impago
(5, '001-001-005', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 1, 1),
(6, '001-001-006', 1, CURRENT_TIMESTAMP, 1, 0, 1, 1, 2, 1),
(7, '001-001-007', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 3, 1),
(8, '001-001-008', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 4, 1),
-- 4x Crédito Parcial
(9, '001-001-009', 1, CURRENT_TIMESTAMP, 1, 50000.0, 2, 1, 1, 1),
(10,'001-001-010', 1, CURRENT_TIMESTAMP, 1, 0,       2, 1, 2, 1),
(11,'001-001-011', 1, CURRENT_TIMESTAMP, 1, 20000.0, 1, 1, 3, 1),
(12,'001-001-012', 1, CURRENT_TIMESTAMP, 1, 10000.0, 2, 1, 4, 1),
-- 4x Crédito Totalmente Pagado
(13,'001-001-013', 1, CURRENT_TIMESTAMP, 1, 0, 1, 1, 1, 1),
(14,'001-001-014', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 2, 1),
(15,'001-001-015', 1, CURRENT_TIMESTAMP, 1, 20000.0, 1, 1, 3, 1),
(16,'001-001-016', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 4, 1);

-- Nota: id_stockfk apunta a la tabla stocks, donde los IDs van del 1 al 6 según las inserciones previas[cite: 2].
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES 
(10, 5000.0, 1, 1), (10, 10000.0, 1, 4),  (10, 3500.0, 2, 2), (10, 3500.0, 2, 3),
(5, 10000.0, 3, 6), (10, 6000.0, 4, 5),   (20, 5000.0, 5, 1), (10, 10000.0, 6, 4),
(20, 3500.0, 7, 2), (10, 10000.0, 8, 6),  (10, 10000.0, 9, 4), (10, 5000.0, 9, 1),
(20, 6000.0, 10, 5), (10, 10000.0, 11, 6),(20, 3500.0, 12, 3), (10, 5000.0, 13, 1),
(10, 10000.0, 14, 4), (20, 6000.0, 15, 5),(10, 10000.0, 16, 6);

INSERT INTO cuotas_compra (estado, monto, fecha, id_comprafk) VALUES 
(1, 50000.0, '2026-11-01', 5), (1, 50000.0, '2026-12-01', 5), (1, 100000.0, '2026-11-01', 6),
(1, 35000.0, '2026-10-01', 7), (1, 35000.0, '2026-11-01', 7), (1, 50000.0, '2026-11-01', 8), (1, 50000.0, '2026-12-01', 8),
(2, 50000.0, '2026-09-01', 9), (1, 50000.0, '2026-10-01', 9), (2, 60000.0, '2026-09-01', 10), (1, 60000.0, '2026-10-01', 10),
(1, 80000.0, '2026-11-01', 11), (2, 30000.0, '2026-09-01', 12), (1, 30000.0, '2026-10-01', 12),
(2, 50000.0, '2026-08-01', 13), (2, 50000.0, '2026-08-01', 14), (2, 50000.0, '2026-09-01', 14),
(2, 100000.0, '2026-09-01', 15), (2, 50000.0, '2026-08-01', 16), (2, 50000.0, '2026-09-01', 16);

INSERT INTO pagos_compra (monto, fecha, tipo, id_comprafk, id_cajafk) VALUES 
(150000.0, CURRENT_TIMESTAMP, 1, 1, 1), (70000.0, CURRENT_TIMESTAMP, 1, 2, 1), 
(50000.0, CURRENT_TIMESTAMP, 1, 3, 1),  (60000.0, CURRENT_TIMESTAMP, 1, 4, 1),
(50000.0, CURRENT_TIMESTAMP, 1, 9, 1),  (20000.0, CURRENT_TIMESTAMP, 1, 11, 1), (10000.0, CURRENT_TIMESTAMP, 1, 12, 1),
(20000.0, CURRENT_TIMESTAMP, 1, 15, 1),
(50000.0, CURRENT_TIMESTAMP, 2, 9, 1),  (60000.0, CURRENT_TIMESTAMP, 2, 10, 1), (30000.0, CURRENT_TIMESTAMP, 2, 12, 1),
(50000.0, CURRENT_TIMESTAMP, 2, 13, 1), (50000.0, CURRENT_TIMESTAMP, 2, 14, 1), (50000.0, CURRENT_TIMESTAMP, 2, 14, 1),
(100000.0, CURRENT_TIMESTAMP, 2, 15, 1),(50000.0, CURRENT_TIMESTAMP, 2, 16, 1), (50000.0, CURRENT_TIMESTAMP, 2, 16, 1);

-- ============================================================
-- 5. VENTAS (16 Casos - Usando PK hexadecimal en el Detalle)
-- ============================================================
INSERT INTO timbrados (id, nro_timbrado, fin_vigencia) VALUES (1, '12345678', '2027-12-31');
INSERT INTO secuencias_venta (id, id_localfk, id_timbradofk, ultimo_nro) VALUES (1, 1, 1, 16);

INSERT INTO ventas (id, fecha, total_cuotas, monto_entrega, tipo_credito, estado, cod_num, id_clientefk, id_secuencias_ventafk) VALUES 
-- 4x Contado
(1, CURRENT_TIMESTAMP, 0, 30000.0, 0, 1, '001-001-001', 1, 1),
(2, CURRENT_TIMESTAMP, 0, 54000.0, 0, 1, '001-001-002', 2, 1),
(3, CURRENT_TIMESTAMP, 0, 19000.0, 0, 1, '001-001-003', 3, 1),
(4, CURRENT_TIMESTAMP, 0, 60000.0, 0, 1, '001-001-004', 4, 1),
-- 4x Crédito Impago
(5, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-005', 1, 1),
(6, CURRENT_TIMESTAMP, 1, 0, 1, 1, '001-001-006', 2, 1),
(7, CURRENT_TIMESTAMP, 1, 0, 1, 1, '001-001-007', 3, 1),
(8, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-008', 4, 1),
-- 4x Crédito Parcial
(9,  CURRENT_TIMESTAMP, 2, 20000.0, 1, 1, '001-001-009', 1, 1),
(10, CURRENT_TIMESTAMP, 2, 0,       1, 1, '001-001-010', 2, 1),
(11, CURRENT_TIMESTAMP, 1, 14000.0, 1, 1, '001-001-011', 3, 1),
(12, CURRENT_TIMESTAMP, 2, 10000.0, 1, 1, '001-001-012', 4, 1),
-- 4x Crédito Totalmente Pagado
(13, CURRENT_TIMESTAMP, 2, 0,       1, 1, '001-001-013', 1, 1),
(14, CURRENT_TIMESTAMP, 1, 0,       1, 1, '001-001-014', 2, 1),
(15, CURRENT_TIMESTAMP, 1, 10000.0, 1, 1, '001-001-015', 3, 1),
(16, CURRENT_TIMESTAMP, 2, 0,       1, 1, '001-001-016', 4, 1);

-- Nota: id_detalleproductofk usa el código hexadecimal[cite: 2]
INSERT INTO detalle_venta (cantidad, precio, id_detalleproductofk, id_ventafk) VALUES 
(1, 20000.0, '1000000D', 1), (1, 10000.0, '1000000A', 1),   
(2, 20000.0, '1000000F', 2), (2, 7000.0,  '1000000C', 2),
(1, 12000.0, '1000000E', 3), (1, 7000.0,  '1000000B', 3),    
(3, 20000.0, '1000000D', 4),
(2, 20000.0, '1000000D', 5), (4, 10000.0, '1000000A', 6),   
(1, 12000.0, '1000000E', 7), (1, 7000.0,  '1000000C', 7),
(2, 20000.0, '1000000F', 8), (2, 20000.0, '1000000D', 9),   
(2, 10000.0, '1000000A', 9), (3, 20000.0, '1000000F', 10),
(4, 7000.0,  '1000000C', 11), (5, 12000.0, '1000000E', 12),  
(2, 20000.0, '1000000D', 13), (1, 20000.0, '1000000F', 14),
(3, 10000.0, '1000000A', 15), (2, 12000.0, '1000000E', 16);

INSERT INTO cuotas_venta (estado, monto, fecha, id_ventafk) VALUES 
(1, 20000.0, '2026-10-01', 5), (1, 20000.0, '2026-11-01', 5), (1, 40000.0, '2026-10-01', 6),
(1, 19000.0, '2026-10-01', 7), (1, 20000.0, '2026-10-01', 8), (1, 20000.0, '2026-11-01', 8),
(2, 20000.0, '2026-09-01', 9), (1, 20000.0, '2026-10-01', 9), (2, 30000.0, '2026-09-01', 10), (1, 30000.0, '2026-10-01', 10),
(1, 14000.0, '2026-10-01', 11), (2, 25000.0, '2026-09-01', 12), (1, 25000.0, '2026-10-01', 12),
(2, 20000.0, '2026-08-01', 13), (2, 20000.0, '2026-09-01', 13), (2, 20000.0, '2026-08-01', 14),
(2, 20000.0, '2026-09-01', 15), (2, 12000.0, '2026-08-01', 16), (2, 12000.0, '2026-09-01', 16);

INSERT INTO pagos_venta (monto, fecha, tipo, id_ventafk, id_cajafk) VALUES 
(30000.0, CURRENT_TIMESTAMP, 1, 1, 1), (54000.0, CURRENT_TIMESTAMP, 1, 2, 1), 
(19000.0, CURRENT_TIMESTAMP, 1, 3, 1), (60000.0, CURRENT_TIMESTAMP, 1, 4, 1),
(20000.0, CURRENT_TIMESTAMP, 1, 9, 1), (14000.0, CURRENT_TIMESTAMP, 1, 11, 1), (10000.0, CURRENT_TIMESTAMP, 1, 12, 1),
(10000.0, CURRENT_TIMESTAMP, 1, 15, 1),
(20000.0, CURRENT_TIMESTAMP, 2, 9, 1), (30000.0, CURRENT_TIMESTAMP, 2, 10, 1), (25000.0, CURRENT_TIMESTAMP, 2, 12, 1),
(20000.0, CURRENT_TIMESTAMP, 2, 13, 1), (20000.0, CURRENT_TIMESTAMP, 2, 13, 1), (20000.0, CURRENT_TIMESTAMP, 2, 14, 1),
(20000.0, CURRENT_TIMESTAMP, 2, 15, 1), (12000.0, CURRENT_TIMESTAMP, 2, 16, 1), (12000.0, CURRENT_TIMESTAMP, 2, 16, 1);

-- ============================================================
-- 6. COMANDAS / ORDENES (16 Casos apuntando a HexPK)
-- ============================================================
INSERT INTO ordenes (estado, cantidad, observacion, id_mesafk, id_clientefk, id_detalleproductofk, tipo, estado_impresion, last_print_error) VALUES 
-- 4x Pendientes
(1, 2, 'Sin mayonesa', 1, 1, '1000000D', 1, 'PENDIENTE', NULL),     -- Hamb 1u
(1, 1, 'Helada',       2, 2, '1000000A', 1, 'PENDIENTE', NULL),     -- Coca 1L
(1, 3, 'Sin sal',      3, 3, '1000000F', 1, 'PENDIENTE', NULL),     -- Papas 1u
(1, 2, NULL,           4, 4, '1000000E', 1, 'PENDIENTE', NULL),     -- Hamb 0.5u
-- 4x En Preparación (Impresas)
(2, 1, 'Llevar a caja',1, 1, '1000000A', 2, 'IMPRESO', NULL),
(2, 2, 'Rápido',       2, 2, '1000000D', 2, 'IMPRESO', NULL),
(2, 1, NULL,           3, 3, '1000000C', 2, 'IMPRESO', NULL),     -- Fanta
(2, 4, 'Cobrar POS',   4, 4, '1000000F', 2, 'IMPRESO', NULL),
-- 4x Completadas
(3, 1, NULL, 1, 1, '1000000B', 1, 'IMPRESO', NULL),
(3, 2, NULL, 2, 2, '1000000D', 1, 'IMPRESO', NULL),
(3, 1, NULL, 3, 3, '1000000E', 1, 'IMPRESO', NULL),
(3, 3, NULL, 4, 4, '1000000C', 1, 'IMPRESO', NULL),
-- 4x Fallo de impresión
(1, 3, NULL, 1, 1, '1000000D', 3, 'FALLO', 'Network timeout at 192.168.1.50'),
(1, 1, NULL, 2, 2, '1000000A', 3, 'FALLO', 'Printer Out of Paper'),
(1, 2, NULL, 3, 3, '1000000F', 3, 'FALLO', 'Connection Refused'),
(1, 5, NULL, 4, 4, '1000000B', 3, 'FALLO', 'Device Offline');

-- ============================================================
-- 7. RESERVAS (16 Casos - Exactamente igual a iteraciones previas)
-- ============================================================
INSERT INTO reservas (estado, cantidad_personas, observacion, fecha_reserva, tiempo_estimado, tiempo_ocupacion, id_mesafk, id_clientefk) VALUES 
(1, 4, 'Cena de negocios', '2026-10-01 20:00:00', '02:00:00', NULL, 1, 1),
(1, 6, 'Cumpleaños',       '2026-10-02 21:00:00', '03:00:00', NULL, 2, 2),
(1, 2, 'Aniversario',      '2026-10-03 19:30:00', '01:30:00', NULL, 3, 3),
(1, 8, 'Despedida',        '2026-10-04 22:00:00', '04:00:00', NULL, 4, 4),
(2, 6, 'Traen torta',      '2026-09-25 19:30:00', '03:00:00', '01:15:00', 1, 3),
(2, 2, 'Llegan tarde',     '2026-09-25 20:00:00', '01:30:00', '00:45:00', 2, 4),
(2, 4, 'Reunión',          '2026-09-25 21:00:00', '02:00:00', '00:10:00', 3, 1),
(2, 8, 'Familia',          '2026-09-25 13:00:00', '02:30:00', '01:50:00', 4, 2),
(3, 2, NULL,               '2026-09-20 20:00:00', '01:30:00', '01:40:00', 1, 4),
(3, 4, NULL,               '2026-09-19 21:00:00', '02:00:00', '02:15:00', 2, 1),
(3, 6, NULL,               '2026-09-18 19:30:00', '03:00:00', '02:50:00', 3, 2),
(3, 2, NULL,               '2026-09-17 22:00:00', '01:00:00', '01:05:00', 4, 3),
(4, 2, 'Llamaron cancelando', '2026-09-24 20:00:00', '01:00:00', NULL, 1, 2),
(4, 4, 'No show',             '2026-09-23 21:00:00', '02:00:00', NULL, 2, 3),
(4, 3, 'Cancelado por lluvia','2026-09-22 19:00:00', '01:30:00', NULL, 3, 4),
(4, 5, 'No show',             '2026-09-21 21:30:00', '02:00:00', NULL, 4, 1);

PRAGMA foreign_keys = ON;