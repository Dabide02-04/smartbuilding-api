import json
from pathlib import Path

from huggingface_hub import snapshot_download

destino = Path("modelos/edad")

snapshot_download(
    repo_id="nateraw/vit-age-classifier",
    local_dir=str(destino),
    allow_patterns=[
        "config.json",
        "preprocessor_config.json",
        "*.safetensors",
    ],
)

configuracion = json.loads(
    (destino / "config.json").read_text()
)

print("Modelo descargado.")
print("Rangos disponibles:", configuracion["id2label"])
