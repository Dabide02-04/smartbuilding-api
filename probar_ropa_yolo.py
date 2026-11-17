from huggingface_hub import hf_hub_download
from ultralytics import YOLO

ruta = hf_hub_download(
    repo_id="HasanKabir23/Yolov26s-DeepFashion2",
    filename="best.pt",
    local_dir="modelos/ropa_yolo",
)

modelo = YOLO(ruta)

resultado = modelo.predict(
    source="/tmp/recorte_prenda_superior.jpg",
    device="cpu",
    imgsz=416,
    conf=0.25,
    verbose=False,
)[0]

for caja in resultado.boxes:
    categoria = modelo.names[int(caja.cls[0].item())]
    puntuacion = float(caja.conf[0].item())
    print(categoria, round(puntuacion * 100, 1), "%")

if len(resultado.boxes) == 0:
    print("No se detectaron prendas con este umbral.")

resultado.save(filename="/tmp/prueba_ropa_yolo.jpg")
