import os
from contextlib import contextmanager

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

import app.main as main


@pytest.fixture
def api():
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smartbuilding_test",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        row_factory=dict_row,
    ) as conexion:
        with conexion.transaction(force_rollback=True):
            edificio = conexion.execute("""
                INSERT INTO edificio (nombre)
                VALUES ('Edificio de pruebas automaticas')
                RETURNING id_edificio
            """).fetchone()

            torre = conexion.execute("""
                INSERT INTO torre (id_edificio, numero)
                VALUES (%s, 1)
                RETURNING id_torre
            """, (edificio["id_edificio"],)).fetchone()

            apartamento = conexion.execute("""
                INSERT INTO apartamento (id_torre, numero, piso)
                VALUES (%s, '101', 1)
                RETURNING id_apartamento
            """, (torre["id_torre"],)).fetchone()

            persona = conexion.execute("""
                INSERT INTO persona (id_apartamento, nombre, tipo)
                VALUES (%s, 'Residente de prueba', 'residente')
                RETURNING id_persona
            """, (apartamento["id_apartamento"],)).fetchone()

            @contextmanager
            def conectar_pruebas():
                with conexion.transaction():
                    yield conexion

            with pytest.MonkeyPatch.context() as parche:
                parche.setattr(main, "conectar", conectar_pruebas)

                with TestClient(main.app) as cliente:
                    yield cliente, persona["id_persona"]
