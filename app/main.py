from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.conexion import conectar
app = FastAPI()
class ResidenteCreate(BaseModel):
    full_name: str
    tower: int
    apartment: int


residentes = [
    {
        "id": 1,
        "full_name": "Juan Perez",
        "tower": 1,
        "apartment": 101
    },
    {
        "id": 2,
        "full_name": "Maria Gomez",
        "tower": 2,
        "apartment": 305
    }
]
@app.get("/")
def root():
    return {"message": "Bienvenido a SmartBuilding API"}
@app.get("/residentes")
def get_residentes(tower: int | None = None):
    with conectar() as conexion:
        resultado = conexion.execute("""
            SELECT
                p.id_persona AS id,
                p.nombre AS full_name,
                t.numero AS tower,
                a.numero AS apartment
            FROM persona AS p
            JOIN apartamento AS a
                ON a.id_apartamento = p.id_apartamento
            JOIN torre AS t
                ON t.id_torre = a.id_torre
           WHERE (%s::integer IS NULL OR t.numero = %s)
           ORDER BY p.id_persona
        """, (tower, tower))
        return resultado.fetchall()
@app.get("/residentes/{residente_id}")
def get_residente_por_id(residente_id: int):
    with conectar() as conexion:
        resultado = conexion.execute("""
            SELECT
                p.id_persona AS id,
                p.nombre AS full_name,
                t.numero AS tower,
                a.numero AS apartment
            FROM persona AS p
            JOIN apartamento AS a
                ON a.id_apartamento = p.id_apartamento
            JOIN torre AS t
                ON t.id_torre = a.id_torre
            WHERE p.id_persona = %s
        """, (residente_id,))
        residente = resultado.fetchone()

    if residente is None:
        raise HTTPException(
            status_code=404,
            detail="Residente no encontrado"
        )

    return residente
@app.post("/residentes", status_code=201)
def crear_residente(residente: ResidenteCreate):
    with conectar() as conexion:
        apartamentos = conexion.execute("""
            SELECT a.id_apartamento
            FROM apartamento AS a
            JOIN torre AS t ON t.id_torre = a.id_torre
            WHERE t.numero = %s AND a.numero = %s
        """, (
            residente.tower,
            str(residente.apartment),
        )).fetchall()

        if not apartamentos:
            raise HTTPException(
                status_code=404,
                detail="Apartamento no encontrado"
            )

        if len(apartamentos) > 1:
            raise HTTPException(
                status_code=409,
                detail="La torre y el apartamento coinciden en varios edificios"
            )

        nuevo = conexion.execute("""
            INSERT INTO persona (id_apartamento, nombre, tipo)
            VALUES (%s, %s, %s)
            RETURNING id_persona
        """, (
            apartamentos[0]["id_apartamento"],
            residente.full_name,
            "residente",
        )).fetchone()

    return get_residente_por_id(nuevo["id_persona"])
@app.put("/residentes/{residente_id}")
def actualizar_residente(
    residente_id: int,
    residente_actualizado: ResidenteCreate,
):
    with conectar() as conexion:
        apartamentos = conexion.execute("""
            SELECT a.id_apartamento
            FROM apartamento AS a
            JOIN torre AS t ON t.id_torre = a.id_torre
            WHERE t.numero = %s AND a.numero = %s
        """, (
            residente_actualizado.tower,
            str(residente_actualizado.apartment),
        )).fetchall()

        if not apartamentos:
            raise HTTPException(
                status_code=404,
                detail="Apartamento no encontrado"
            )

        if len(apartamentos) > 1:
            raise HTTPException(
                status_code=409,
                detail="La torre y el apartamento coinciden en varios edificios"
            )

        actualizado = conexion.execute("""
            UPDATE persona
            SET nombre = %s, id_apartamento = %s
            WHERE id_persona = %s
            RETURNING id_persona
        """, (
            residente_actualizado.full_name,
            apartamentos[0]["id_apartamento"],
            residente_id,
        )).fetchone()

        if actualizado is None:
            raise HTTPException(
                status_code=404,
                detail="Residente no encontrado"
            )

    return get_residente_por_id(residente_id)
@app.delete("/residentes/{residente_id}", status_code=204)
def eliminar_residente(residente_id: int):
    with conectar() as conexion:
        eliminado = conexion.execute("""
            DELETE FROM persona
            WHERE id_persona = %s
            RETURNING id_persona
        """, (residente_id,)).fetchone()

        if eliminado is None:
            raise HTTPException(
                status_code=404,
                detail="Residente no encontrado"
            )
