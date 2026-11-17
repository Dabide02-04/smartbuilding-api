from functools import lru_cache
from pathlib import Path

from ultralytics import YOLO

RUTA = Path("/home/debian/smartbuilding-api/modelos/ropa_yolo/best.pt")

SUPERIORES = {
    "short_sleeve_top": "Prenda de manga corta",
    "long_sleeve_top": "Prenda de manga larga",
    "short_sleeve_outwear": "Abrigo de manga corta",
    "long_sleeve_outwear": "Abrigo de manga larga",
    "vest": "Chaleco",
    "sling": "Top de tirantes",
}

INFERIORES = {
    "shorts": "Pantalon corto",
    "trousers": "Pantalon",
    "skirt": "Falda",
}

VESTIDOS = {
    "short_sleeve_dress": "Vestido de manga corta",
    "long_sleeve_dress": "Vestido de manga larga",
    "vest_dress": "Vestido sin mangas",
    "sling_dress": "Vestido de tirantes",
}


@lru_cache(maxsize=1)
def cargar_ropa():
    return YOLO(str(RUTA))


def prendas_persona(imagen, recuadro):
    respuesta = {
        "superior": "No estimable",
        "inferior": "No estimable",
    }

    alto, ancho = imagen.shape[:2]
    x1, y1, x2, y2 = [int(valor) for valor in recuadro]

    x1 = max(0, min(ancho, x1))
    x2 = max(0, min(ancho, x2))
    y1 = max(0, min(alto, y1))
    y2 = max(0, min(alto, y2))

    cuerpo = imagen[y1:y2, x1:x2]
    h, w = cuerpo.shape[:2]

    if h < 80 or w < 40:
        return respuesta

    modelo = cargar_ropa()

    resultado = modelo.predict(
        source=cuerpo,
        device="cpu",
        imgsz=416,
        conf=0.40,
        verbose=False,
    )[0]

    mejores = {"superior": 0.0, "inferior": 0.0}
    vestido = None
    confianza_vestido = 0.0

    for caja in resultado.boxes:
        categoria = modelo.names[int(caja.cls[0].item())]
        confianza = float(caja.conf[0].item())
        _, arriba, _, abajo = caja.xyxy[0].tolist()
        centro = ((arriba + abajo) / 2) / h

        if categoria in VESTIDOS:
            if confianza > confianza_vestido:
                vestido = VESTIDOS[categoria]
                confianza_vestido = confianza

        elif categoria in SUPERIORES and centro < 0.70:
            if confianza > mejores["superior"]:
                mejores["superior"] = confianza
                respuesta["superior"] = SUPERIORES[categoria]

        elif categoria in INFERIORES and centro > 0.40:
            if y2 < alto - 2 and confianza > mejores["inferior"]:
                mejores["inferior"] = confianza
                respuesta["inferior"] = INFERIORES[categoria]

    if vestido and confianza_vestido > max(mejores.values()):
        respuesta["superior"] = vestido
        respuesta["inferior"] = "Misma prenda: vestido"

    return respuesta
