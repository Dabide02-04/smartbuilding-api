BEGIN;

WITH nuevo_edificio AS (
    INSERT INTO edificio (nombre)
    VALUES ('Edificio de prueba')
    RETURNING id_edificio
),
nueva_torre AS (
    INSERT INTO torre (id_edificio, numero)
    SELECT id_edificio, 1 FROM nuevo_edificio
    RETURNING id_torre
),
nuevo_apartamento AS (
    INSERT INTO apartamento (id_torre, numero, piso)
    SELECT id_torre, '101', 1 FROM nueva_torre
    RETURNING id_apartamento
)
INSERT INTO persona (id_apartamento, nombre, tipo)
SELECT id_apartamento, nombre_prueba, 'residente'
FROM nuevo_apartamento
CROSS JOIN (
    VALUES ('Persona de prueba A'), ('Persona de prueba B')
) AS ejemplos(nombre_prueba);

COMMIT;
