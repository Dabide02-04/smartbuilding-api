BEGIN;
-- =====================================================
-- 1. EDIFICIO
-- =====================================================
CREATE TABLE edificio (
 id_edificio INTEGER GENERATED ALWAYS AS IDENTITY,
 nombre VARCHAR(100) NOT NULL,
 CONSTRAINT pk_edificio
 PRIMARY KEY (id_edificio)
);
-- =====================================================
-- 2. TORRE
-- Un edificio puede tener varias torres.
-- =====================================================
CREATE TABLE torre (
 id_torre INTEGER GENERATED ALWAYS AS IDENTITY,
 id_edificio INTEGER NOT NULL,
 numero INTEGER NOT NULL,
 CONSTRAINT pk_torre
 PRIMARY KEY (id_torre),
 CONSTRAINT fk_torre_edificio
 FOREIGN KEY (id_edificio)
 REFERENCES edificio(id_edificio)
 ON DELETE CASCADE,
 CONSTRAINT uq_torre_edificio_numero
 UNIQUE (id_edificio, numero),
 CONSTRAINT ck_torre_numero
 CHECK (numero > 0)
);
-- =====================================================
-- 3. APARTAMENTO
-- Una torre puede contener varios apartamentos.
-- =====================================================
CREATE TABLE apartamento (
 id_apartamento INTEGER GENERATED ALWAYS AS IDENTITY,
 id_torre INTEGER NOT NULL,
 numero VARCHAR(10) NOT NULL,
 piso INTEGER NOT NULL,
 CONSTRAINT pk_apartamento
 PRIMARY KEY (id_apartamento),
 CONSTRAINT fk_apartamento_torre
 FOREIGN KEY (id_torre)
 REFERENCES torre(id_torre)
 ON DELETE CASCADE,
 CONSTRAINT uq_apartamento_torre_numero
 UNIQUE (id_torre, numero),
 CONSTRAINT ck_apartamento_piso
 CHECK (piso > 0)
);
-- =====================================================
-- 4. PERSONA
-- Una persona pertenece a un solo apartamento.
-- Un apartamento puede alojar varias personas.
-- =====================================================
CREATE TABLE persona (
 id_persona INTEGER GENERATED ALWAYS AS IDENTITY,
 id_apartamento INTEGER NOT NULL,
 nombre VARCHAR(100) NOT NULL,
 telefono VARCHAR(20),
 email VARCHAR(150),
 tipo VARCHAR(20) NOT NULL,
 CONSTRAINT pk_persona
 PRIMARY KEY (id_persona),
 CONSTRAINT fk_persona_apartamento
 FOREIGN KEY (id_apartamento)
 REFERENCES apartamento(id_apartamento)
 ON DELETE CASCADE,
 CONSTRAINT ck_persona_tipo
 CHECK (tipo IN ('propietario', 'residente'))
);
-- =====================================================
-- 5. MASCOTA
-- Las mascotas se asocian con el apartamento.
-- Si un apartamento no tiene mascota, no se crea fila.
-- =====================================================
CREATE TABLE mascota (
 id_mascota INTEGER GENERATED ALWAYS AS IDENTITY,
 id_apartamento INTEGER NOT NULL,
 tipo VARCHAR(30) NOT NULL,
 CONSTRAINT pk_mascota
 PRIMARY KEY (id_mascota),
 CONSTRAINT fk_mascota_apartamento
 FOREIGN KEY (id_apartamento)
 REFERENCES apartamento(id_apartamento)
 ON DELETE CASCADE
);
-- =====================================================
-- 6. CASILLERO
-- Cada apartamento puede tener como máximo un casillero.
-- =====================================================
CREATE TABLE casillero (
 id_casillero INTEGER GENERATED ALWAYS AS IDENTITY,
 id_apartamento INTEGER NOT NULL,
 codigo VARCHAR(20) NOT NULL,
 CONSTRAINT pk_ca
 PRIMARY KEY (id_casillero),
 CONSTRAINT fk_casillero_apartamento
 FOREIGN KEY (id_apartamento)
 REFERENCES apartamento(id_apartamento)
 ON DELETE CASCADE,
 CONSTRAINT uq_casillero_apartamento
 UNIQUE (id_apartamento),
 CONSTRAINT uq_casillero_codigo
 UNIQUE (codigo)
);
-- =====================================================
-- 7. PARQUEADERO
-- Un apartamento puede tener varios parqueaderos.
-- =====================================================
CREATE TABLE parqueadero (
 id_parqueadero INTEGER GENERATED ALWAYS AS IDENTITY,
 id_apartamento INTEGER NOT NULL,
 codigo VARCHAR(20) NOT NULL,
 CONSTRAINT pk_parqueadero
 PRIMARY KEY (id_parqueadero),
 CONSTRAINT fk_parqueadero_apartamento
 FOREIGN KEY (id_apartamento)
 REFERENCES apartamento(id_apartamento)
 ON DELETE CASCADE,
 CONSTRAINT uq_parqueadero_codigo
 UNIQUE (codigo)
);
-- =====================================================
-- 8. VEHÍCULO
-- Un parqueadero puede estar libre o tener un vehículo.
-- Si está libre, no se crea una fila en esta tabla.
-- =====================================================
CREATE TABLE vehiculo (
 id_vehiculo INTEGER GENERATED ALWAYS AS IDENTITY,
 id_parqueadero INTEGER NOT NULL,
 placa VARCHAR(10) NOT NULL,
 CONSTRAINT pk_vehiculo
 PRIMARY KEY (id_vehiculo),
 CONSTRAINT fk_vehiculo_parqueadero
 FOREIGN KEY (id_parqueadero)
 REFERENCES parqueadero(id_parqueadero)
 ON DELETE CASCADE,
 CONSTRAINT uq_vehiculo_parqueadero
 UNIQUE (id_parqueadero),
 CONSTRAINT uq_vehiculo_placa
 UNIQUE (placa)
 );
-- Índices para agilizar las búsquedas mediante llaves foráneas.
CREATE INDEX idx_torre_edificio
 ON torre(id_edificio);
CREATE INDEX idx_apartamento_torre
 ON apartamento(id_torre);
CREATE INDEX idx_persona_apartamento
 ON persona(id_apartamento);
CREATE INDEX idx_mascota_apartamento
 ON mascota(id_apartamento);
CREATE INDEX idx_parqueadero_apartamento
 ON parqueadero(id_apartamento);
COMMIT;