from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
    if tower is None:
        return residentes

    return [
        residente
        for residente in residentes
        if residente["tower"] == tower
    ]

@app.get("/residentes/{residente_id}")
def get_residente_por_id(residente_id: int):
    for residente in residentes:
        if residente["id"] == residente_id:
            return residente

    raise HTTPException(
        status_code=404,
        detail="Residente no encontrado"
    )
@app.post("/residentes", status_code=201)
def crear_residente(residente: ResidenteCreate):
    nuevo_residente = {
        "id": len(residentes) + 1,
        "full_name": residente.full_name,
        "tower": residente.tower,
        "apartment": residente.apartment
    }

    residentes.append(nuevo_residente)

    return nuevo_residente
@app.put("/residentes/{residente_id}")
def actualizar_residente(residente_id: int, residente_actualizado: ResidenteCreate):
    for residente in residentes:
        if residente["id"] == residente_id:
            residente["full_name"] = residente_actualizado.full_name
            residente["tower"] = residente_actualizado.tower
            residente["apartment"] = residente_actualizado.apartment

            return residente

    raise HTTPException(
        status_code=404,
        detail="Residente no encontrado"
    )
@app.delete("/residentes/{residente_id}", status_code=204)
def eliminar_residente(residente_id: int):
    for residente in residentes:
        if residente["id"] == residente_id:
            residentes.remove(residente)
            return

    raise HTTPException(
        status_code=404,
        detail="Residente no encontrado"
    )
