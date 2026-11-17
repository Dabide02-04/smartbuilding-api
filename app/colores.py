import cv2
import numpy as np


def color_dominante(region):
    if region.size == 0 or min(region.shape[:2]) < 8:
        return "No estimable"

    reducida = cv2.resize(region, (64, 64))
    hsv = cv2.cvtColor(reducida, cv2.COLOR_BGR2HSV)
    tono, saturacion, brillo = cv2.split(hsv)

    nombres = [
        "Rojo", "Naranja", "Amarillo", "Verde", "Azul",
        "Morado", "Rosa", "Marron", "Gris", "Blanco", "Negro",
    ]

    etiquetas = np.zeros(tono.shape, dtype=np.uint8)

    etiquetas[(tono >= 10) & (tono < 25)] = 1
    etiquetas[(tono >= 25) & (tono < 35)] = 2
    etiquetas[(tono >= 35) & (tono < 85)] = 3
    etiquetas[(tono >= 85) & (tono < 130)] = 4
    etiquetas[(tono >= 130) & (tono < 155)] = 5
    etiquetas[(tono >= 155) & (tono < 170)] = 6

    marron = (
        (tono >= 10) & (tono < 25)
        & (brillo < 155) & (saturacion >= 60)
    )
    etiquetas[marron] = 7
    etiquetas[saturacion < 45] = 8
    etiquetas[(saturacion < 45) & (brillo >= 190)] = 9
    etiquetas[brillo < 55] = 10

    cantidades = np.bincount(
        etiquetas.ravel(), minlength=len(nombres)
    )
    ganador = int(cantidades.argmax())
    proporcion = cantidades[ganador] / etiquetas.size

    if proporcion < 0.35:
        return "Varios colores"

    return nombres[ganador]


def colores_persona(imagen, recuadro):
    alto, ancho = imagen.shape[:2]
    x1, y1, x2, y2 = [int(valor) for valor in recuadro]

    x1 = max(0, min(ancho, x1))
    x2 = max(0, min(ancho, x2))
    y1 = max(0, min(alto, y1))
    y2 = max(0, min(alto, y2))

    cuerpo = imagen[y1:y2, x1:x2]
    h, w = cuerpo.shape[:2]

    if h < 40 or w < 20:
        return {
            "superior": "No estimable",
            "inferior": "No estimable",
        }

    torso = cuerpo[
        int(h * 0.25):int(h * 0.50),
        int(w * 0.25):int(w * 0.75),
    ]

    piernas = cuerpo[
        int(h * 0.60):int(h * 0.88),
        int(w * 0.20):int(w * 0.80),
    ]

    return {
        "superior": color_dominante(torso),
        "inferior": (
            "No estimable"
            if y2 >= alto - 2
            else color_dominante(piernas)
        ),
    }
