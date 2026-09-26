-- ============================================================
-- ESTRUCTURA DE BASE DE DATOS (Adaptada para Turso / libSQL)
-- ============================================================

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS cuotas_compra;
DROP TABLE IF EXISTS pagos_compra;
DROP TABLE IF EXISTS reservas;
DROP TABLE IF EXISTS ordenes;
DROP TABLE IF EXISTS egresos;
DROP TABLE IF EXISTS detalle_compra;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS pagos_venta;
DROP TABLE IF EXISTS cuotas_venta;
DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS secuencias_venta;
DROP TABLE IF EXISTS timbrados;
DROP TABLE IF EXISTS cajas;
DROP VIEW IF EXISTS detalles_producto_con_stock;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS mesas;
DROP TABLE IF EXISTS locales;
DROP TABLE IF EXISTS vendedores;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS ingredientes;
DROP TABLE IF EXISTS detalles_precio;
DROP TABLE IF EXISTS detalles_producto;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS precios;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS marcas;
DROP TABLE IF EXISTS permisos_roles;
DROP TABLE IF EXISTS permisos;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS personas;

PRAGMA foreign_keys = ON;

-- ----------------------------
-- Tabla: personas
-- ----------------------------
CREATE TABLE personas (
    cedula       INTEGER PRIMARY KEY,
    nombres      TEXT NOT NULL,
    apellidos    TEXT NOT NULL,
    telefono     INTEGER,
    direccion    TEXT,
    nacionalidad TEXT,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: roles
-- ----------------------------
CREATE TABLE roles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    observacion  TEXT,
    estado       INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: permisos
-- ----------------------------
CREATE TABLE permisos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    estado       INTEGER NOT NULL DEFAULT 1,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: permisos_roles
-- ----------------------------
CREATE TABLE permisos_roles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    crear        INTEGER NOT NULL, -- 0 = false, 1 = true
    editar       INTEGER NOT NULL,
    eliminar     INTEGER NOT NULL,
    leer         INTEGER NOT NULL,
    id_permisofk INTEGER NOT NULL,
    id_rolfk     INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_permisofk) REFERENCES permisos (id),
    FOREIGN KEY (id_rolfk) REFERENCES roles (id)
);

-- ----------------------------
-- Tabla: marcas
-- ----------------------------
CREATE TABLE marcas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    estado       INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: categorias
-- ----------------------------
CREATE TABLE categorias (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    descripcion  TEXT,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    estado       INTEGER NOT NULL
);

-- ----------------------------
-- Tabla: precios
-- ----------------------------
CREATE TABLE precios (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    monto        REAL NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    valido_desde TEXT NOT NULL,
    valido_hasta TEXT
);

-- ----------------------------
-- Tabla: productos
-- ----------------------------
CREATE TABLE productos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT NOT NULL,
    descripcion    TEXT,
    estado         INTEGER NOT NULL,
    impuesto       INTEGER NOT NULL,
    pesable        INTEGER NOT NULL DEFAULT 0,
    perecedero     INTEGER NOT NULL DEFAULT 0,
    costeo         INTEGER,
    unidad_medida  TEXT NOT NULL,
    es_ingrediente INTEGER,
    es_comida      INTEGER,
    id_categoriafk INTEGER NOT NULL,
    id_marcafk     INTEGER NOT NULL,
    fecha_creado   TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_categoriafk) REFERENCES categorias (id),
    FOREIGN KEY (id_marcafk) REFERENCES marcas (id)
);

-- ----------------------------
-- Tabla: detalles_producto
-- ----------------------------
CREATE TABLE detalles_producto (
    cod_barra       TEXT PRIMARY KEY,
    unidad_por_lote INTEGER NOT NULL,
    color           TEXT,
    tamanho         INTEGER,
    id_productofk   INTEGER NOT NULL,
    fecha_creado    TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_productofk) REFERENCES productos (id)
);

-- ----------------------------
-- Tabla: detalles_precio
-- ----------------------------
CREATE TABLE detalles_precio (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_preciofk          INTEGER NOT NULL,
    id_detalleproductofk TEXT NOT NULL,
    fecha_creado         TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_preciofk) REFERENCES precios (id),
    FOREIGN KEY (id_detalleproductofk) REFERENCES detalles_producto (cod_barra)
);

-- ----------------------------
-- Tabla: ingredientes
-- ----------------------------
CREATE TABLE ingredientes (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad                  INTEGER NOT NULL,
    unidad_medida             TEXT NOT NULL,
    id_producto_ingredientefk INTEGER NOT NULL,
    id_producto_finalfk       INTEGER NOT NULL,
    fecha_creado              TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_producto_ingredientefk) REFERENCES productos (id),
    FOREIGN KEY (id_producto_finalfk) REFERENCES productos (id)
);

-- ----------------------------
-- Tabla: usuarios
-- ----------------------------
CREATE TABLE usuarios (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    contra       TEXT NOT NULL,
    alias        TEXT NOT NULL,
    estado       INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    id_rolfk     INTEGER NOT NULL,
    id_personafk INTEGER NOT NULL,
    FOREIGN KEY (id_rolfk) REFERENCES roles (id),
    FOREIGN KEY (id_personafk) REFERENCES personas (cedula)
);

-- ----------------------------
-- Tabla: proveedores
-- ----------------------------
CREATE TABLE proveedores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    id_personafk INTEGER NOT NULL,
    razon_social TEXT NOT NULL,
    ruc          INTEGER NOT NULL,
    correo       TEXT,
    estado       INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_personafk) REFERENCES personas (cedula)
);

-- ----------------------------
-- Tabla: clientes
-- ----------------------------
CREATE TABLE clientes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    id_personafk   INTEGER NOT NULL,
    ruc            INTEGER,
    razon_social   TEXT,
    persona_fisica INTEGER NOT NULL,
    fecha_creado   TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_personafk) REFERENCES personas (cedula)
);

-- ----------------------------
-- Tabla: vendedores
-- ----------------------------
CREATE TABLE vendedores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    salario      REAL NOT NULL,
    comision     REAL,
    cod_num      TEXT,
    estado       INTEGER NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    id_usuariofk INTEGER NOT NULL,
    FOREIGN KEY (id_usuariofk) REFERENCES usuarios (id)
);

-- ----------------------------
-- Tabla: locales
-- ----------------------------
CREATE TABLE locales (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    direccion    TEXT,
    cod_num      TEXT,
    telefono     TEXT,
    estado       INTEGER NOT NULL DEFAULT 1,
    latitud      REAL,
    longitud     REAL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: mesas
-- ----------------------------
CREATE TABLE mesas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    estado       INTEGER DEFAULT 1,
    capacidad    INTEGER NOT NULL,
    id_localfk   INTEGER NOT NULL,
    id_clientefk INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    ocupado_desde TEXT,
    FOREIGN KEY (id_localfk) REFERENCES locales (id),
    FOREIGN KEY (id_clientefk) REFERENCES clientes (id)
);

-- ----------------------------
-- Tabla: stocks
-- ----------------------------
CREATE TABLE stocks (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    cant_deposito        INTEGER NOT NULL,
    cant_mostrador       INTEGER NOT NULL,
    cant_reservado       INTEGER NOT NULL,
    lote                 TEXT,
    fecha_vencimiento    TEXT,
    id_detalleproductofk TEXT NOT NULL,
    id_localfk           INTEGER NOT NULL,
    fecha_creado         TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_detalleproductofk) REFERENCES detalles_producto (cod_barra),
    FOREIGN KEY (id_localfk) REFERENCES locales (id)
);

-- Vista de detalles de producto con stock disponible
CREATE VIEW detalles_producto_con_stock AS
SELECT
    dp.cod_barra,
    dp.unidad_por_lote,
    dp.color,
    dp.tamanho,
    dp.id_productofk,
    dp.fecha_creado,
    COALESCE(
        SUM(COALESCE(s.cant_mostrador, 0) + COALESCE(s.cant_deposito, 0)),
        0
    ) AS stock_total
FROM detalles_producto AS dp
LEFT JOIN stocks AS s ON s.id_detalleproductofk = dp.cod_barra
GROUP BY
    dp.cod_barra,
    dp.unidad_por_lote,
    dp.color,
    dp.tamanho,
    dp.id_productofk,
    dp.fecha_creado;

-- ----------------------------
-- Tabla: cajas
-- ----------------------------
CREATE TABLE cajas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_creado   TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    fecha_cierre   TEXT,
    monto_apertura REAL NOT NULL,
    monto_cierre   REAL,
    id_usuariofk   INTEGER NOT NULL,
    FOREIGN KEY (id_usuariofk) REFERENCES usuarios (id)
);

-- ----------------------------
-- Tabla: timbrados
-- ----------------------------
CREATE TABLE timbrados (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nro_timbrado TEXT NOT NULL,
    fin_vigencia TEXT NOT NULL,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

-- ----------------------------
-- Tabla: secuencias_venta
-- ----------------------------
CREATE TABLE secuencias_venta (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_localfk    INTEGER,
    id_vendedorfk INTEGER,
    id_timbradofk INTEGER,
    ultimo_nro    INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (id_localfk) REFERENCES locales (id),
    FOREIGN KEY (id_vendedorfk) REFERENCES vendedores (id),
    FOREIGN KEY (id_timbradofk) REFERENCES timbrados (id)
);

-- ----------------------------
-- Tabla: ventas
-- ----------------------------
CREATE TABLE ventas (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha                 TEXT NOT NULL,
    total_cuotas          INTEGER,
    monto_entrega         REAL DEFAULT 0,
    tipo_credito          INTEGER,
    estado                INTEGER NOT NULL,
    cod_num               TEXT,
    clima                 INTEGER,
    temperatura           INTEGER,
    humedad               INTEGER,
    velocidad_viento      REAL,
    lluvia                REAL,
    precipitaciones       REAL,
    evento_festivo        INTEGER,
    cantidad_personas     INTEGER,
    ocupacion             TEXT,
    id_clientefk          INTEGER NOT NULL,
    id_cobradorfk         INTEGER,
    id_secuencias_ventafk INTEGER NOT NULL,
    fecha_creado          TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_clientefk) REFERENCES clientes (id)
);

-- ----------------------------
-- Tabla: detalle_venta
-- ----------------------------
CREATE TABLE detalle_venta (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad             INTEGER NOT NULL,
    precio               REAL NOT NULL,
    descuento            REAL,
    id_detalleproductofk TEXT NOT NULL,
    id_ventafk           INTEGER NOT NULL,
    fecha_creado         TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_detalleproductofk) REFERENCES detalles_producto (cod_barra),
    FOREIGN KEY (id_ventafk) REFERENCES ventas (id)
);

-- ----------------------------
-- Tabla: cuotas_venta
-- ----------------------------
CREATE TABLE cuotas_venta (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    estado       INTEGER NOT NULL DEFAULT 1,
    monto        REAL,
    fecha        TEXT NOT NULL,
    descuento    REAL,
    interes      INTEGER,
    id_ventafk   INTEGER,
    id_usuariofk INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_ventafk) REFERENCES ventas (id)
);

-- ----------------------------
-- Tabla: pagos_venta
-- ----------------------------
CREATE TABLE pagos_venta (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    estado       INTEGER NOT NULL DEFAULT 1,
    tipo         INTEGER DEFAULT 1,
    monto        REAL NOT NULL,
    fecha        TEXT NOT NULL,
    id_ventafk   INTEGER,
    id_cajafk    INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_cajafk) REFERENCES cajas (id),
    FOREIGN KEY (id_ventafk) REFERENCES ventas (id)
);

-- ----------------------------
-- Tabla: compras
-- ----------------------------
CREATE TABLE compras (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nro            TEXT,
    id_localfk     INTEGER NOT NULL,
    fecha          TEXT NOT NULL,
    estado         INTEGER NOT NULL,
    monto_entrega  REAL DEFAULT 0,
    total_cuotas   INTEGER,
    tipo_credito   INTEGER NOT NULL,
    fecha_creado   TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    id_proveedorfk INTEGER NOT NULL,
    id_cajafk      INTEGER NOT NULL,
    FOREIGN KEY (id_cajafk) REFERENCES cajas (id),
    FOREIGN KEY (id_localfk) REFERENCES locales (id),
    FOREIGN KEY (id_proveedorfk) REFERENCES proveedores (id)
);

-- ----------------------------
-- Tabla: detalle_compra
-- ----------------------------
CREATE TABLE detalle_compra (
    id_detalle_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad          INTEGER NOT NULL,
    precio            REAL NOT NULL,
    id_comprafk       INTEGER NOT NULL,
    id_stockfk        INTEGER NOT NULL,
    fecha_creado      TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_comprafk) REFERENCES compras (id),
    FOREIGN KEY (id_stockfk) REFERENCES stocks (id)
);

-- ----------------------------
-- Tabla: egresos
-- ----------------------------
CREATE TABLE egresos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    estado       INTEGER NOT NULL DEFAULT 1,
    monto        REAL NOT NULL,
    descripcion  TEXT,
    fecha        TEXT NOT NULL,
    id_cajafk    INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_cajafk) REFERENCES cajas (id)
);

-- ----------------------------
-- Tabla: ordenes
-- ----------------------------
CREATE TABLE ordenes (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    estado               INTEGER NOT NULL DEFAULT 1,
    cantidad             INTEGER NOT NULL DEFAULT 1,
    observacion          TEXT,
    id_mesafk            INTEGER NOT NULL,
    id_usuariofk         INTEGER,
    id_clientefk         INTEGER,
    id_detalleproductofk TEXT,
    id_preciofk          INTEGER,
    tipo                 INTEGER NOT NULL DEFAULT 1,
    estado_impresion     TEXT NOT NULL DEFAULT 'PENDIENTE',
    last_print_error     TEXT,
    fecha_creado         TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_mesafk) REFERENCES mesas (id),
    FOREIGN KEY (id_preciofk) REFERENCES precios (id),
    FOREIGN KEY (id_detalleproductofk) REFERENCES detalles_producto (cod_barra),
    CHECK (estado_impresion IN ('PENDIENTE', 'IMPRESO', 'FALLO'))
);

-- ----------------------------
-- Tabla: reservas
-- ----------------------------
CREATE TABLE reservas (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    estado            INTEGER NOT NULL DEFAULT 1,
    cantidad_personas INTEGER NOT NULL DEFAULT 1,
    observacion       TEXT,
    fecha_reserva     TEXT NOT NULL,
    tiempo_estimado   TEXT,
    tiempo_ocupacion  TEXT,
    id_mesafk         INTEGER NOT NULL,
    id_usuariofk      INTEGER,
    id_clientefk      INTEGER,
    fecha_creado      TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_mesafk) REFERENCES mesas (id),
    FOREIGN KEY (id_clientefk) REFERENCES clientes (id)
);

-- ----------------------------
-- Tabla: cuotas_compra
-- ----------------------------
CREATE TABLE cuotas_compra (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    estado       INTEGER NOT NULL DEFAULT 1,
    monto        REAL,
    fecha        TEXT NOT NULL,
    descuento    REAL,
    interes      INTEGER,
    id_comprafk  INTEGER,
    id_usuariofk INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_comprafk) REFERENCES compras (id)
);

-- ----------------------------
-- Tabla: pagos_compra
-- ----------------------------
CREATE TABLE pagos_compra (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    estado       INTEGER NOT NULL DEFAULT 1,
    monto        REAL,
    fecha        TEXT NOT NULL,
    tipo         INTEGER DEFAULT 1,
    id_comprafk  INTEGER,
    id_cajafk    INTEGER,
    fecha_creado TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    FOREIGN KEY (id_cajafk) REFERENCES cajas (id),
    FOREIGN KEY (id_comprafk) REFERENCES compras (id)
);

-- ----------------------------
-- Triggers (Automatización en Turso)
-- ----------------------------
DROP TRIGGER IF EXISTS trg_crear_mesa_delivery;
CREATE TRIGGER trg_crear_mesa_delivery
AFTER INSERT ON locales
FOR EACH ROW
BEGIN
    INSERT INTO mesas (nombre, estado, capacidad, id_localfk)
    VALUES ('Delivery/Retiro', 1, 0, NEW.id);
END;

-- ----------------------------
-- Datos Iniciales
-- ----------------------------
INSERT INTO personas (cedula, nombres, apellidos) VALUES 
(1, 'Cliente', 'Ocasional'), 
(4360067, 'Alejandro', 'Alvarez');

INSERT INTO roles (id, nombre, observacion, estado) VALUES
(1, 'Admin', 'Acceso Total', 1);

INSERT INTO permisos (id, nombre, estado) VALUES 
(1, 'Usuario', 1), (2, 'Rol', 1), (3, 'Permiso_rol', 1), (4, 'Producto', 1), 
(5, 'Categoria', 1), (6, 'Marca', 1), (7, 'Precio', 1), (8, 'Ingrediente', 1), 
(9, 'Cliente', 1), (10, 'Proveedor', 1), (11, 'Vendedor', 1), (12, 'Local', 1), 
(13, 'Mesa', 1), (14, 'Stock', 1), (15, 'Caja', 1), (16, 'Venta', 1), 
(17, 'Cuota_venta', 1), (18, 'Pago_venta', 1), (19, 'Compra', 1), 
(20, 'Cuota_compra', 1), (21, 'Pago_compra', 1), (22, 'Egreso', 1), 
(23, 'Orden', 1), (24, 'Reserva', 1);

INSERT INTO permisos_roles (crear, editar, eliminar, leer, id_permisofk, id_rolfk)
SELECT 
    1 AS crear,
    1 AS editar,
    1 AS eliminar,
    1 AS leer,
    p.id AS id_permisofk,
    1 AS id_rolfk
FROM permisos p
WHERE NOT EXISTS (
    SELECT 1 
    FROM permisos_roles pr
    WHERE pr.id_permisofk = p.id AND pr.id_rolfk = 1
);

INSERT INTO usuarios (id, contra, alias, estado, id_rolfk, id_personafk) VALUES 
(1, 'scrypt$pQDitONnZE/sjyQuLA373w==$3qTf0pWmVEm36W5957vaqUXTmH8dTbjsB65un1+sd3o=', 'admin', 1, 1, 4360067);

INSERT INTO marcas (id, nombre, estado) VALUES 
(1, 'Sin Marca', 1);

INSERT INTO clientes (id, id_personafk, persona_fisica) VALUES
(1, 1, 1);

INSERT INTO locales (id, nombre) VALUES
(1, 'Central');
