from pathlib import Path
from app.ropa import prendas_persona
from threading import Lock
from app.colores import colores_persona
from app.edad import estimar_edad
import cv2
import numpy as np
from fastapi import APIRouter, Body, HTTPException
from ultralytics import YOLO

router = APIRouter(prefix="/vision", tags=["Detector"])

modelo = None
bloqueo = Lock()
ruta_modelo = Path(__file__).resolve().parent.parent / "yolo26n.pt"


@router.post("/detectar")
def detectar(imagen: bytes = Body(media_type="image/jpeg")):
    global modelo

    if not imagen:
        raise HTTPException(400, "La imagen esta vacia")

    if len(imagen) > 2 * 1024 * 1024:
        raise HTTPException(413, "La imagen supera los 2 MB")

    datos = np.frombuffer(imagen, dtype=np.uint8)
    cuadro = cv2.imdecode(datos, cv2.IMREAD_COLOR)

    if cuadro is None:
        raise HTTPException(400, "No se pudo leer la imagen")

    alto, ancho = cuadro.shape[:2]

    if max(alto, ancho) > 4096:
        raise HTTPException(400, "La imagen es demasiado grande")

    with bloqueo:
        if modelo is None:
            if not ruta_modelo.is_file():
                raise HTTPException(
                    503, "No se encuentra el modelo yolo26n.pt"
                )
            modelo = YOLO(str(ruta_modelo))

        resultado = modelo.predict(
            source=cuadro,
            classes=[0],
            device="cpu",
            imgsz=416,
            conf=0.35,
            verbose=False,
        )[0]

        personas = []

        for caja in resultado.boxes:
            recuadro = caja.xyxy[0].tolist()
            colores = colores_persona(cuadro, recuadro)
            prendas = prendas_persona(cuadro, recuadro)

            personas.append({
                "recuadro": recuadro,
                "confianza": float(caja.conf[0]),
                "color_superior": colores["superior"],
                "color_inferior": colores["inferior"],
		"edad_estimada": estimar_edad(cuadro, recuadro),
		"prenda_superior": prendas["superior"],
                "prenda_inferior": prendas["inferior"],
            })

    return {
        "ancho": ancho,
        "alto": alto,
        "total": len(personas),
        "personas": personas,
    }
