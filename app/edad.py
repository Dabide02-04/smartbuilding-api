from functools import lru_cache
from pathlib import Path

import cv2
import torch
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)

RUTA = Path("/home/debian/smartbuilding-api/modelos/edad")

detector_caras = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


@lru_cache(maxsize=1)
def cargar_modelo():
    procesador = AutoImageProcessor.from_pretrained(
        str(RUTA),
        local_files_only=True,
        use_fast=False,
    )

    modelo = AutoModelForImageClassification.from_pretrained(
        str(RUTA),
        local_files_only=True,
        use_safetensors=True,
    )
    modelo.eval()

    return procesador, modelo


def estimar_edad(imagen, recuadro):
    alto, ancho = imagen.shape[:2]
    x1, y1, x2, y2 = [int(valor) for valor in recuadro]

    x1 = max(0, min(ancho, x1))
    x2 = max(0, min(ancho, x2))
    y1 = max(0, min(alto, y1))
    y2 = max(0, min(alto, y2))

    if x2 <= x1 or y2 <= y1:
        return "No estimable"

    limite = y1 + int((y2 - y1) * 0.55)
    zona = imagen[y1:limite, x1:x2]

    if zona.size == 0 or min(zona.shape[:2]) < 64:
        return "No estimable"

    gris = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)

    caras = detector_caras.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(64, 64),
    )

    if len(caras) != 1:
        return "No estimable"

    x, y, w, h = caras[0]
    rostro = zona[y:y + h, x:x + w]
    rostro = cv2.cvtColor(rostro, cv2.COLOR_BGR2RGB)

    procesador, modelo = cargar_modelo()
    entrada = procesador(images=rostro, return_tensors="pt")

    with torch.inference_mode():
        puntuaciones = modelo(**entrada).logits.softmax(dim=-1)[0]

    indice = int(puntuaciones.argmax().item())

    if float(puntuaciones[indice].item()) < 0.5:
        return "No concluyente"

    etiqueta = modelo.config.id2label[indice]

    if etiqueta == "more than 70":
        return "Mas de 70 anos"

    return etiqueta + " anos"
