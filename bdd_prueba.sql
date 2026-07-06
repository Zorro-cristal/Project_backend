-- ============================================================
-- 1. PERSONAS (15 Registros: Staff, Clientes, Proveedores)
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
-- 2. ROLES, PERMISOS Y USUARIOS
-- ============================================================
INSERT INTO roles (id, nombre, observacion, estado) VALUES
(1, 'Admin', 'Acceso Total', 1),
(2, 'Cajero', 'Caja y Cobros', 1),
(3, 'Mozo', 'Atención en salón', 1),
(4, 'Gerente', 'Reportes y auditoría', 1),
(5, 'Cocinero', 'Visualización de comandas', 1);

INSERT INTO permisos (id, nombre) VALUES 
(1, 'Facturación'), (2, 'Inventario'), (3, 'Usuarios'), (4, 'Reportes'), (5, 'Compras');

INSERT INTO permisos_roles (crear, editar, eliminar, leer, id_permisofk, id_rolfk) VALUES
(true, true, true, true, 1, 1), (true, true, true, true, 2, 1),
(true, false, false, true, 1, 2), (false, false, false, true, 2, 2),
(true, true, false, true, 1, 3);

INSERT INTO usuarios (id, contra, alias, estado, id_rolfk, id_personafk) VALUES
(1, 'hash1', 'admin', 1, 1, 1000001),
(2, 'hash2', 'ana_caja', 1, 2, 1000002),
(3, 'hash3', 'luis_caja2', 1, 2, 1000003),
(4, 'hash4', 'marta_mozo', 1, 3, 1000004),
(5, 'hash5', 'diego_mozo', 1, 3, 1000005);

-- ============================================================
-- 3. CLIENTES, PROVEEDORES Y VENDEDORES (5 de cada uno)
-- ============================================================
INSERT INTO clientes (id, id_personafk, ruc, razon_social, persona_fisica) VALUES
(1, 3000001, 30000018, 'Juan Pérez', 1),
(2, 3000002, 30000029, 'María López', 1),
(3, 3000003, null, 'Carlos Gómez', 1),
(4, 3000004, 80012345, 'Constructora XYZ S.A.', 0),
(5, 3000005, null, 'Sin Nombre', 1);

INSERT INTO proveedores (id, id_personafk, razon_social, ruc, correo, estado) VALUES
(1, 2000001, 'Distri Guairá S.A.', 80000011, 'ventas@guaira.com', true),
(2, 2000002, 'Frigorífico Villarrica', 80000022, 'carne@frigo.com', true),
(3, 2000003, 'Bebidas Unidas S.R.L.', 80000033, 'pedidos@bebidas.com', true),
(4, 2000004, 'Insumos Gastronómicos', 80000044, 'insumos@gastro.com', true),
(5, 2000005, 'Granja San José', 80000055, 'huevos@sanjose.com', true);

INSERT INTO vendedores (id, salario, comision, cod_num, estado, id_personafk) VALUES
(1, 3000000, 3.5, 'V01', true, 1000004),
(2, 3000000, 3.5, 'V02', true, 1000005),
(3, 3500000, 5.0, 'V03', true, 1000001),
(4, 2800000, 2.0, 'V04', false, 1000002),
(5, 2800000, 2.0, 'V05', true, 1000003);

-- ============================================================
-- 4. LOCALES Y MESAS (5+ Permutaciones de estado)
-- ============================================================
INSERT INTO locales (id, nombre, direccion, cod_num, telefono, estado, latitud, longitud) VALUES
(1, 'Local Principal', 'Bvr. Yegros', 'L01', '021000111', true, -25.78, -56.43),
(2, 'Sucursal Ybaroty', 'Barrio Ybaroty', 'L02', '021000222', true, -25.79, -56.44);

INSERT INTO mesas (id, nombre, estado, capacidad, id_localfk, id_clientefk) VALUES
(1, 'Mesa 1', true, 4, 1, null),       -- Libre
(2, 'Mesa 2', false, 2, 1, 1),        -- Ocupada por Juan Pérez
(3, 'Mesa 3', true, 6, 1, null),       -- Libre
(4, 'Mesa 4', false, 4, 1, 2),        -- Ocupada por María
(5, 'Mesa 5 VIP', true, 8, 1, null),   -- Libre VIP
(6, 'Mesa 1 (Suc 2)', true, 4, 2, null);

-- ============================================================
-- 5. CATEGORÍAS, MARCAS Y PRODUCTOS (Cruces Varios)
-- ============================================================
INSERT INTO categorias (id, nombre, descripcion, estado) VALUES
(1, 'Bebidas Frías', 'Cervezas, Gaseosas, Jugos', 1),
(2, 'Parrilla', 'Carnes y asados', 1),
(3, 'Comidas Típicas', 'Sopa, Chipa Guasu, Mbeju', 1),
(4, 'Insumos', 'Materia prima', 1),
(5, 'Postres', 'Dulces y helados', 1);

INSERT INTO marcas (id, nombre, estado) VALUES 
(1, 'Pilsen', 1), (2, 'Coca-Cola', 1), (3, 'Guaraní', 1), (4, 'Casero', 1), (5, 'Lactolanda', 1);

INSERT INTO productos (id, nombre, estado, impuesto, pesable, perecedero, unidad_medida, es_ingrediente, es_comida, id_categoriafk, id_marcafk) VALUES
(1, 'Cerveza Pilsen 1L', 1, 10, false, false, 'Unidad', false, false, 1, 1),
(2, 'Asado de Tira', 1, 5, true, true, 'Kg', false, true, 2, 3),
(3, 'Sopa Paraguaya', 1, 5, false, true, 'Porción', false, true, 3, 4),
(4, 'Harina de Maíz', 1, 5, true, false, 'Kg', true, false, 4, 4),
(5, 'Queso Paraguay', 1, 5, true, true, 'Kg', true, false, 4, 5),
(6, 'Gaseosa 2L', 1, 10, false, false, 'Unidad', false, false, 1, 2),
(7, 'Helado Artesanal', 1, 10, false, true, 'Porción', false, true, 5, 4);

-- DETALLES Y PRECIOS
INSERT INTO detalles_producto (cod_barra, unidad_por_lote, id_productofk) VALUES
('7840001001', 12, 1), ('2000000001', 1, 2), ('7840001002', 1, 3), 
('2000000002', 1, 4), ('2000000003', 1, 5), ('7840001003', 6, 6), ('7840001004', 1, 7);

INSERT INTO precios (id, monto, valido_desde) VALUES
(1, 15000, NOW() - INTERVAL '60 days'), (2, 55000, NOW() - INTERVAL '60 days'), 
(3, 12000, NOW() - INTERVAL '60 days'), (4, 8000, NOW() - INTERVAL '60 days'), 
(5, 35000, NOW() - INTERVAL '60 days'), (6, 14000, NOW() - INTERVAL '60 days'), 
(7, 10000, NOW() - INTERVAL '60 days');

INSERT INTO detalles_precio (id_preciofk, id_detalleproductofk) VALUES
(1, '7840001001'), (2, '2000000001'), (3, '7840001002'), (4, '2000000002'), 
(5, '2000000003'), (6, '7840001003'), (7, '7840001004');

-- INGREDIENTES (La Sopa Paraguaya usa Harina de Maíz y Queso)
INSERT INTO ingredientes (cantidad, unidad_medida, id_producto_ingredientefk, id_producto_finalfk) VALUES
(200, 'Gramos', 4, 3), (150, 'Gramos', 5, 3);

-- STOCKS
INSERT INTO stocks (id, cant_deposito, cant_mostrador, cant_reservado, id_detalleproductofk, id_localfk) VALUES
(1, 100, 24, 0, '7840001001', 1), (2, 50, 10, 0, '2000000001', 1),
(3, 0, 20, 0, '7840001002', 1),  (4, 20, 0, 0, '2000000002', 1),
(5, 10, 5, 0, '2000000003', 1),   (6, 60, 12, 0, '7840001003', 1),
(7, 0, 30, 0, '7840001004', 1);

-- ============================================================
-- 6. CAJAS (2 Cajas Abiertas)
-- ============================================================
INSERT INTO cajas (id, monto_apertura, id_usuariofk) VALUES
(1, 500000, 2), (2, 300000, 3);

-- ============================================================
-- 7. 5 PERMUTACIONES DE VENTAS (Clima, Crédito/Contado, Entregas)
-- ============================================================
-- Venta 1: CONTADO - Día de CALOR EXTREMO (39°C, WMO 0). Venta de mucha bebida.
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, clima, temperatura, humedad, evento, id_clientefk, id_localfk, id_usuariofk, id_vendedorfk) VALUES
(1, '001-001', NOW() - INTERVAL '5 days', 0, 0, false, 1, 0, 39, 45, false, 5, 1, 2, 1);
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(15, 15000, 0, '7840001001', 1), (5, 14000, 0, '7840001003', 1);
INSERT INTO pagos_venta (tipo, monto, fecha, id_ventafk, id_cajafk) VALUES (1, 295000, NOW() - INTERVAL '5 days', 1, 1);

-- Venta 2: CRÉDITO SIN ENTREGA (2 cuotas) - Día FRÍO (10°C, WMO 3). Comida caliente.
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, clima, temperatura, humedad, evento, id_clientefk, id_localfk, id_usuariofk, id_vendedorfk) VALUES
(2, '001-002', NOW() - INTERVAL '4 days', 2, 0, true, 1, 3, 10, 85, false, 4, 1, 2, 2);
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(10, 12000, 0, '7840001002', 2), (2, 55000, 0, '2000000001', 2); -- 120mil + 110mil = 230mil
INSERT INTO cuotas_venta (monto, fecha, descuento, interes, id_ventafk, id_usuariofk) VALUES
(115000, NOW() + INTERVAL '15 days', 0, 0, 2, 2), (115000, NOW() + INTERVAL '30 days', 0, 0, 2, 2);

-- Venta 3: CRÉDITO CON ENTREGA INICIAL - Día TORMENTA (22°C, WMO 95). Cliente particular.
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, clima, temperatura, humedad, evento, id_clientefk, id_localfk, id_usuariofk, id_vendedorfk) VALUES
(3, '001-003', NOW() - INTERVAL '3 days', 1, 50000, true, 1, 95, 22, 95, false, 1, 1, 3, 1);
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(3, 55000, 0, '2000000001', 3); -- 165mil total. Entrega 50mil, saldo 115mil.
INSERT INTO pagos_venta (tipo, monto, fecha, id_ventafk, id_cajafk) VALUES (1, 50000, NOW() - INTERVAL '3 days', 3, 2);
INSERT INTO cuotas_venta (monto, fecha, descuento, interes, id_ventafk, id_usuariofk) VALUES (115000, NOW() + INTERVAL '7 days', 0, 0, 3, 3);

-- Venta 4: CONTADO - CLIMA AGRADABLE CON EVENTO (Día de la Madre)
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, clima, temperatura, humedad, evento, id_clientefk, id_localfk, id_usuariofk, id_vendedorfk) VALUES
(4, '001-004', NOW() - INTERVAL '1 days', 0, 0, false, 1, 1, 24, 60, true, 2, 1, 2, 2);
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(4, 10000, 0, '7840001004', 4), (2, 12000, 0, '7840001002', 4);
INSERT INTO pagos_venta (tipo, monto, fecha, id_ventafk, id_cajafk) VALUES (1, 64000, NOW() - INTERVAL '1 days', 4, 1);

-- Venta 5: CONTADO CON DESCUENTO APLICADO - Día Nublado
INSERT INTO ventas (id, nro, fecha, total_cuotas, monto_entrega, tipo_credito, estado, clima, temperatura, humedad, evento, id_clientefk, id_localfk, id_usuariofk, id_vendedorfk) VALUES
(5, '001-005', NOW(), 0, 0, false, 1, 3, 20, 70, false, 3, 1, 3, 1);
INSERT INTO detalle_venta (cantidad, precio, descuento, id_detalleproductofk, id_ventafk) VALUES
(5, 15000, 5000, '7840001001', 5); -- Llevó 5, se le descontó 5000 al total.
INSERT INTO pagos_venta (tipo, monto, fecha, id_ventafk, id_cajafk) VALUES (1, 70000, NOW(), 5, 2);

-- ============================================================
-- 8. 5 PERMUTACIONES DE COMPRAS (Proveedores, Contado/Crédito)
-- ============================================================
-- Compra 1: CONTADO - Insumos perecederos
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(1, 'FAC-P01', 1, NOW() - INTERVAL '10 days', 1, 0, 0, false, 4, 1);
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES (50, 6000, 1, 4); -- Harina
INSERT INTO pagos_compra (monto, fecha, id_comprafk, id_cajafk) VALUES (300000, NOW() - INTERVAL '10 days', 1, 1);

-- Compra 2: CRÉDITO 3 CUOTAS SIN ENTREGA - Bebidas
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(2, 'FAC-P02', 1, NOW() - INTERVAL '8 days', 1, 0, 3, true, 3, 1);
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES (200, 10000, 2, 1); -- Cerveza (2 Millones)
INSERT INTO cuotas_compra (monto, fecha, interes, id_comprafk, id_usuariofk) VALUES 
(666666, NOW() + INTERVAL '22 days', 0, 2, 1), (666667, NOW() + INTERVAL '52 days', 0, 2, 1), (666667, NOW() + INTERVAL '82 days', 0, 2, 1);

-- Compra 3: CRÉDITO CON ENTREGA - Carne
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(3, 'FAC-P03', 1, NOW() - INTERVAL '2 days', 1, 500000, 1, true, 2, 1);
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES (30, 45000, 3, 2); -- Carne (1.35 Millones)
INSERT INTO pagos_compra (monto, fecha, id_comprafk, id_cajafk) VALUES (500000, NOW() - INTERVAL '2 days', 3, 1);
INSERT INTO cuotas_compra (monto, fecha, interes, id_comprafk, id_usuariofk) VALUES (850000, NOW() + INTERVAL '13 days', 0, 3, 1);

-- Compra 4: CONTADO - Varios Productos
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(4, 'FAC-P04', 1, NOW() - INTERVAL '1 days', 1, 0, 0, false, 1, 2);
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES (20, 10000, 4, 6), (10, 25000, 4, 5); 
INSERT INTO pagos_compra (monto, fecha, id_comprafk, id_cajafk) VALUES (450000, NOW() - INTERVAL '1 days', 4, 2);

-- Compra 5: CRÉDITO 1 CUOTA - Insumos varios
INSERT INTO compras (id, nro, id_localfk, fecha, estado, monto_entrega, total_cuotas, tipo_credito, id_proveedorfk, id_cajafk) VALUES
(5, 'FAC-P05', 1, NOW(), 1, 0, 1, true, 5, 2);
INSERT INTO detalle_compra (cantidad, precio, id_comprafk, id_stockfk) VALUES (10, 15000, 5, 5);
INSERT INTO cuotas_compra (monto, fecha, interes, id_comprafk, id_usuariofk) VALUES (150000, NOW() + INTERVAL '30 days', 0, 5, 1);

-- ============================================================
-- 9. 5 RESERVAS (Diferentes estados y cantidades)
-- ============================================================
INSERT INTO reservas (estado, cantidad_personas, observacion, fecha_reserva, id_mesafk, id_usuariofk, id_clientefk) VALUES
(1, 4, 'Cerca de la ventana', NOW() + INTERVAL '2 hours', 1, 2, 1),
(1, 8, 'Cumpleaños', NOW() + INTERVAL '1 day', 5, 2, 4),
(0, 2, 'Cancelada por el cliente', NOW() - INTERVAL '1 day', 2, 3, 3),
(2, 6, 'Reserva completada (Ya comieron)', NOW() - INTERVAL '2 days', 3, 2, 2),
(1, 4, 'Traer sillita de bebé', NOW() + INTERVAL '3 hours', 6, 3, 5);

-- ============================================================
-- 10. 5 ÓRDENES (Comandas en diferentes mesas y estados)
-- ============================================================
-- Estado 1: Pendiente (Cocina/Barra), Estado 2: Entregado
INSERT INTO ordenes (estado, cantidad, observacion, id_mesafk, id_usuariofk, id_detalleproductofk, id_preciofk) VALUES
(1, 2, 'Asado bien cocido', 2, 4, '2000000001', 2),
(2, 2, 'Cervezas frías', 2, 4, '7840001001', 1),
(1, 4, 'Sopa sin bordes quemados', 4, 5, '7840001002', 3),
(2, 1, 'Gaseosa natural', 4, 5, '7840001003', 6),
(1, 2, 'Helado para después', 4, 5, '7840001004', 7);

-- ============================================================
-- 11. 5 EGRESOS (Gastos operativos comunes)
-- ============================================================
INSERT INTO egresos (estado, monto, descripcion, fecha, id_cajafk) VALUES
(1, 25000, 'Compra de hielo en estación de servicio', NOW() - INTERVAL '2 days', 1),
(1, 50000, 'Anticipo salario mozo Diego', NOW() - INTERVAL '1 day', 1),
(1, 35000, 'Pago por flete / delivery', NOW(), 2),
(1, 150000, 'Pago ANDE / Recarga de saldo', NOW(), 1),
(1, 40000, 'Artículos de limpieza varios', NOW(), 2);