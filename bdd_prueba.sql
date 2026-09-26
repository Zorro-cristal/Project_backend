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

-- Limpiamos solo los registros de prueba, manteniendo tus IDs = 1
DELETE FROM clientes WHERE id > 1;
DELETE FROM locales WHERE id > 1;
DELETE FROM marcas WHERE id > 1;
-- Mantenemos intactas a las personas base (Cliente Ocasional y Alejandro)
DELETE FROM personas WHERE cedula NOT IN (1, 4360067);

-- ============================================================
-- 1. ACTUALIZACIÓN LOCAL BASE Y CAJA
-- ============================================================
UPDATE locales SET cod_num = '001', latitud = -25.7500, longitud = -56.4333 WHERE id = 1;

INSERT INTO locales (id, nombre, cod_num, latitud, longitud) VALUES
(2, 'Sucursal Norte', '002', -25.7500, -56.4333);

INSERT INTO cajas (id, fecha_creado, monto_apertura, monto_cierre, id_usuariofk) VALUES 
(1, CURRENT_TIMESTAMP, 500000.00, NULL, 1);

INSERT INTO mesas (id, nombre, estado, capacidad, id_localfk) VALUES
(1, 'Mesa 1', 1, 4, 1), (2, 'Mesa 2', 1, 2, 1), (3, 'Mesa 3', 1, 6, 1), (4, 'Mesa 4', 1, 4, 1);

-- ============================================================
-- 2. PERSONAS, CLIENTES Y PROVEEDORES
-- ============================================================
-- Insertamos directamente usando la cédula (PK)
INSERT INTO personas (cedula, nombres, apellidos, telefono, direccion, nacionalidad) VALUES 
(2000002, 'Maria', 'Gomez', NULL, 'Barrio Centro', 'PRY'),
(2000003, 'Carlos', 'Lopez', '971654321', NULL, 'PRY'),
(2000004, 'Ana', 'Martinez', NULL, NULL, 'ARG'),
(3000001, 'Distribuidora', 'Sur', '982111222', 'Ruta 8 km 2', 'PRY'),
(3000002, 'Carnes', 'Premium', NULL, 'Mercado Central', 'PRY'),
(3000003, 'Bebidas', 'S.A.', '973333444', NULL, 'PRY'),
(3000004, 'Empaques', 'Global', NULL, NULL, 'PRY');

-- El Cliente 1 (Ocasional) ya existe. Insertamos del 2 al 4 usando las cédulas como FK.
INSERT INTO clientes (id, id_personafk, ruc, razon_social, persona_fisica) VALUES
(2, 2000002, 0, NULL, 1),                
(3, 2000003, NULL, 'Carlos Lopez', 1),   
(4, 2000004, 7, 'Ana Martinez', 1);      

-- Proveedores usando cédulas como FK.
INSERT INTO proveedores (id, id_personafk, razon_social, ruc, correo, estado) VALUES
(1, 3000001, 'Distribuidora Sur S.A.', 5, 'ventas@dsur.com.py', 1),
(2, 3000002, 'Carnes Premium', 8, NULL, 1),
(3, 3000003, 'Bebidas S.A.', 1, 'contacto@bebidas.com', 1),
(4, 3000004, 'Empaques Global', 4, NULL, 1);

-- ============================================================
-- 3. CATÁLOGO, STOCKS Y PRECIOS
-- ============================================================
INSERT INTO categorias (id, nombre, estado) VALUES 
(1, 'Comidas Rápidas', 1), (2, 'Bebidas', 1);

INSERT INTO marcas (id, nombre, estado) VALUES 
(2, 'Coca-Cola', 1), (3, 'Casero', 1);

INSERT INTO productos (id, nombre, estado, impuesto, pesable, perecedero, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES 
(1, 'Hamburguesa Completa', 1, 10, 0, 1, 'UN', 0, 1, 1, 3), 
(2, 'Coca Cola 500ml', 1, 10, 0, 0, 'UN', 0, 0, 2, 2);      

INSERT INTO detalles_producto (id, cod_barra, unidad_por_lote, id_productofk) VALUES 
(1, '7840001000012', 1, 1), 
(2, '7840001000029', 24, 2);

INSERT INTO precios (id, monto, valido_desde) VALUES 
(1, 25000.00, '2026-01-01'), (2, 7000.00, '2026-01-01');

INSERT INTO detalles_precio (id_preciofk, id_detalleproductofk) VALUES 
(1, 1), (2, 2);

INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, id_detalleproductofk, id_localfk) VALUES 
(1, 100, 50, 0, 1, 1), (2, 100, 24, 0, 2, 1);

-- ============================================================
-- 4. COMPRAS (16 Registros: 4x Contado, 4x Impago, 4x Parcial, 4x Pagado)
-- ============================================================
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES 
(1, '001-001-00001', 1, CURRENT_TIMESTAMP, 1, 150000.0, 0, 0, 1, 1),
(2, '001-001-00002', 1, CURRENT_TIMESTAMP, 1, 50000.0,  0, 0, 2, 1),
(3, '001-001-00003', 1, CURRENT_TIMESTAMP, 1, 80000.0,  0, 0, 3, 1),
(4, '001-001-00004', 1, CURRENT_TIMESTAMP, 1, 120000.0, 0, 0, 4, 1),
(5, '001-001-00005', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 1, 1),
(6, '001-001-00006', 1, CURRENT_TIMESTAMP, 1, 0, 1, 1, 2, 1),
(7, '001-001-00007', 1, CURRENT_TIMESTAMP, 1, 0, 3, 1, 3, 1),
(8, '001-001-00008', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 4, 1),
(9, '001-001-00009', 1, CURRENT_TIMESTAMP, 1, 50000.0, 2, 1, 1, 1),
(10, '001-001-00010', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 2, 1),
(11, '001-001-00011', 1, CURRENT_TIMESTAMP, 1, 20000.0, 1, 1, 3, 1),
(12, '001-001-00012', 1, CURRENT_TIMESTAMP, 1, 0, 3, 1, 4, 1),
(13, '001-001-00013', 1, CURRENT_TIMESTAMP, 1, 0, 1, 1, 1, 1),
(14, '001-001-00014', 1, CURRENT_TIMESTAMP, 1, 0, 2, 1, 2, 1),
(15, '001-001-00015', 1, CURRENT_TIMESTAMP, 1, 0, 1, 1, 3, 1),
(16, '001-001-00016', 1, CURRENT_TIMESTAMP, 1, 0, 3, 1, 4, 1);

INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES 
(10, 15000.0, 1, 1), (5, 10000.0, 2, 2), (8, 10000.0, 3, 1), (12, 10000.0, 4, 2),
(10, 20000.0, 5, 1), (5, 30000.0, 6, 2), (10, 15000.0, 7, 1), (8, 25000.0, 8, 2),
(10, 25000.0, 9, 1), (10, 20000.0, 10, 2), (10, 10000.0, 11, 1), (15, 20000.0, 12, 2),
(5, 20000.0, 13, 1), (4, 25000.0, 14, 2), (2, 50000.0, 15, 1), (6, 15000.0, 16, 2);

INSERT INTO cuotas_compra (estado, monto, fecha, id_comprafk) VALUES 
(1, 100000.0, '2026-11-01', 5), (1, 100000.0, '2026-12-01', 5),
(1, 150000.0, '2026-11-01', 6),
(1, 50000.0, '2026-10-01', 7), (1, 50000.0, '2026-11-01', 7), (1, 50000.0, '2026-12-01', 7),
(1, 100000.0, '2026-11-01', 8), (1, 100000.0, '2026-12-01', 8),
(1, 100000.0, '2026-11-01', 9),  (1, 100000.0, '2026-12-01', 9),
(2, 100000.0, '2026-09-01', 10), (1, 100000.0, '2026-10-01', 10),
(1, 80000.0,  '2026-11-01', 11),
(2, 100000.0, '2026-08-01', 12), (2, 100000.0, '2026-09-01', 12), (1, 100000.0, '2026-10-01', 12),
(2, 100000.0, '2026-08-01', 13),
(2, 50000.0,  '2026-08-01', 14), (2, 50000.0, '2026-09-01', 14),
(2, 100000.0, '2026-09-01', 15),
(2, 30000.0,  '2026-07-01', 16), (2, 30000.0, '2026-08-01', 16), (2, 30000.0, '2026-09-01', 16);

INSERT INTO pagos_compra (monto, fecha, tipo, id_comprafk, id_cajafk) VALUES 
(150000.0, CURRENT_TIMESTAMP, 1, 1, 1), (50000.0, CURRENT_TIMESTAMP, 1, 2, 1), 
(80000.0, CURRENT_TIMESTAMP, 1, 3, 1),  (120000.0, CURRENT_TIMESTAMP, 1, 4, 1),
(50000.0, CURRENT_TIMESTAMP, 1, 9, 1), (20000.0, CURRENT_TIMESTAMP, 1, 11, 1),
(100000.0, CURRENT_TIMESTAMP, 2, 10, 1), 
(100000.0, CURRENT_TIMESTAMP, 2, 12, 1), (100000.0, CURRENT_TIMESTAMP, 2, 12, 1),
(100000.0, CURRENT_TIMESTAMP, 2, 13, 1),
(50000.0, CURRENT_TIMESTAMP, 2, 14, 1), (50000.0, CURRENT_TIMESTAMP, 2, 14, 1),
(100000.0, CURRENT_TIMESTAMP, 2, 15, 1),
(30000.0, CURRENT_TIMESTAMP, 2, 16, 1), (30000.0, CURRENT_TIMESTAMP, 2, 16, 1), (30000.0, CURRENT_TIMESTAMP, 2, 16, 1);

-- ============================================================
-- 5. VENTAS (16 Registros Predictivos)
-- ============================================================
INSERT INTO timbrados (id, nro_timbrado, fin_vigencia) VALUES (1, '12345678', '2027-12-31');
INSERT INTO secuencias_venta (id, id_localfk, id_timbradofk, ultimo_nro) VALUES (1, 1, 1, 16);

INSERT INTO ventas (id, fecha, total_cuotas, monto_entrega, tipo_credito, estado, cod_num, clima, temperatura, humedad, lluvia, precipitaciones, evento_festivo, id_clientefk, id_secuencias_ventafk) VALUES 
(1, CURRENT_TIMESTAMP, 0, 32000.0, 0, 1, '001-001-0000001', 1, 35, 40, 0, 0.0, 0, 1, 1),
(2, CURRENT_TIMESTAMP, 0, 25000.0, 0, 1, '001-001-0000002', 2, 22, 65, 0, 0.0, 1, 2, 1),
(3, CURRENT_TIMESTAMP, 0, 64000.0, 0, 1, '001-001-0000003', 3, 18, 90, 1, 15.5, 0, 3, 1),
(4, CURRENT_TIMESTAMP, 0, 14000.0, 0, 1, '001-001-0000004', 1, 28, 50, 0, 0.0, 0, 4, 1),
(5, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-0000005', 3, 15, 95, 1, 30.0, 0, 1, 1),
(6, CURRENT_TIMESTAMP, 1, 0, 1, 1, '001-001-0000006', 1, 38, 30, 0, 0.0,  1, 2, 1),
(7, CURRENT_TIMESTAMP, 3, 0, 1, 1, '001-001-0000007', 2, 25, 70, 0, 0.0,  0, 3, 1),
(8, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-0000008', 3, 12, 85, 1, 10.0, 0, 4, 1),
(9,  CURRENT_TIMESTAMP, 2, 25000.0, 1, 1, '001-001-0000009', 1, 30, 45, 0, 0.0, 0, 1, 1),
(10, CURRENT_TIMESTAMP, 2, 0,       1, 1, '001-001-0000010', 2, 20, 60, 0, 0.0, 0, 2, 1),
(11, CURRENT_TIMESTAMP, 3, 25000.0, 1, 1, '001-001-0000011', 3, 18, 90, 1, 5.0, 1, 3, 1),
(12, CURRENT_TIMESTAMP, 3, 0,       1, 1, '001-001-0000012', 1, 33, 40, 0, 0.0, 0, 4, 1),
(13, CURRENT_TIMESTAMP, 1, 0, 1, 1, '001-001-0000013', 1, 36, 35, 0, 0.0, 1, 1, 1),
(14, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-0000014', 2, 21, 55, 0, 0.0, 0, 2, 1),
(15, CURRENT_TIMESTAMP, 1, 0, 1, 1, '001-001-0000015', 3, 19, 88, 1, 12.0, 0, 3, 1),
(16, CURRENT_TIMESTAMP, 2, 0, 1, 1, '001-001-0000016', 1, 29, 42, 0, 0.0, 0, 4, 1);

INSERT INTO detalle_venta (cantidad, precio, id_detalleproductofk, id_ventafk) VALUES 
(1, 25000.0, 1, 1), (1, 7000.0, 2, 1), (1, 25000.0, 1, 2), (2, 25000.0, 1, 3), 
(2, 7000.0, 2, 3), (2, 7000.0, 2, 4),
(4, 25000.0, 1, 5), (5, 7000.0, 2, 6), (3, 25000.0, 1, 7), (2, 25000.0, 1, 8),
(3, 25000.0, 1, 9), (4, 25000.0, 1, 10), (4, 25000.0, 1, 11), (3, 25000.0, 1, 12),
(2, 25000.0, 1, 13), (4, 25000.0, 1, 14), (1, 25000.0, 1, 15), (2, 25000.0, 1, 16);

INSERT INTO cuotas_venta (estado, monto, fecha, id_ventafk) VALUES 
(1, 50000.0, '2026-10-01', 5), (1, 50000.0, '2026-11-01', 5),
(1, 35000.0, '2026-10-01', 6),
(1, 25000.0, '2026-10-01', 7), (1, 25000.0, '2026-11-01', 7), (1, 25000.0, '2026-12-01', 7),
(1, 25000.0, '2026-10-01', 8), (1, 25000.0, '2026-11-01', 8),
(2, 25000.0, '2026-09-01', 9),  (1, 25000.0, '2026-10-01', 9),
(2, 50000.0, '2026-09-01', 10), (1, 50000.0, '2026-10-01', 10),
(2, 25000.0, '2026-08-01', 11), (2, 25000.0, '2026-09-01', 11), (1, 25000.0, '2026-10-01', 11),
(2, 25000.0, '2026-09-01', 12), (1, 25000.0, '2026-10-01', 12), (1, 25000.0, '2026-11-01', 12),
(2, 50000.0, '2026-08-01', 13), (2, 50000.0, '2026-08-01', 14), (2, 50000.0, '2026-09-01', 14),
(2, 25000.0, '2026-09-01', 15), (2, 25000.0, '2026-08-01', 16), (2, 25000.0, '2026-09-01', 16);

INSERT INTO pagos_venta (monto, fecha, tipo, id_ventafk, id_cajafk) VALUES 
(32000.0, CURRENT_TIMESTAMP, 1, 1, 1), (25000.0, CURRENT_TIMESTAMP, 1, 2, 1), 
(64000.0, CURRENT_TIMESTAMP, 1, 3, 1), (14000.0, CURRENT_TIMESTAMP, 1, 4, 1),
(25000.0, CURRENT_TIMESTAMP, 1, 9, 1), (25000.0, CURRENT_TIMESTAMP, 1, 11, 1),
(25000.0, CURRENT_TIMESTAMP, 2, 9, 1), (50000.0, CURRENT_TIMESTAMP, 2, 10, 1),
(25000.0, CURRENT_TIMESTAMP, 2, 11, 1), (25000.0, CURRENT_TIMESTAMP, 2, 11, 1),
(25000.0, CURRENT_TIMESTAMP, 2, 12, 1),
(50000.0, CURRENT_TIMESTAMP, 2, 13, 1), (50000.0, CURRENT_TIMESTAMP, 2, 14, 1), 
(50000.0, CURRENT_TIMESTAMP, 2, 14, 1), (25000.0, CURRENT_TIMESTAMP, 2, 15, 1),
(25000.0, CURRENT_TIMESTAMP, 2, 16, 1), (25000.0, CURRENT_TIMESTAMP, 2, 16, 1);

-- ============================================================
-- 6. ORDENES Y RESERVAS
-- ============================================================
INSERT INTO ordenes (estado, cantidad, observacion, id_mesafk, id_clientefk, id_detalleproductofk, tipo, estado_impresion, last_print_error) VALUES 
(1, 2, 'Sin mayonesa', 1, 1, 1, 1, 'PENDIENTE', NULL),
(1, 1, NULL,           2, 2, 2, 1, 'PENDIENTE', NULL),
(1, 3, 'Bien cocido',  3, 3, 1, 1, 'PENDIENTE', NULL),
(3, 1, 'Llamar al llegar', 1, 1, 2, 2, 'IMPRESO', NULL),
(2, 3, NULL, 1, 1, 1, 3, 'FALLO', 'Network timeout at 192.168.1.50'),
(5, 1, NULL, 1, 1, 2, 1, 'IMPRESO', NULL);

INSERT INTO reservas (estado, cantidad_personas, observacion, fecha_reserva, tiempo_estimado, tiempo_ocupacion, id_mesafk, id_clientefk) VALUES 
(1, 4, 'Cena de negocios', '2026-10-01 20:00:00', '02:00:00', '02:15:00', 1, 1),
(1, 6, 'Cumpleaños',       '2026-10-02 21:00:00', '03:00:00', '02:45:00', 2, 2),
(2, 6, 'Traen torta',      '2026-09-25 19:30:00', NULL, '03:15:00', 1, 3),
(3, 4, NULL,               '2026-09-19 21:00:00', NULL, NULL, 2, 1);

PRAGMA foreign_keys = ON;