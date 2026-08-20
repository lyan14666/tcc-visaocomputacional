from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "weapons.pt"

CAMERA_SOURCE = 0
CAMERA_NAME = "CAMERA 01 - ENTRADA PRINCIPAL"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CAMERA_BUFFER_SIZE = 1

YOLO_IMAGE_SIZE = 640
WEAPON_CONFIDENCE = 0.45
IOU_THRESHOLD = 0.45

# Na sua máquina AMD Vega 6 vamos começar assim.
# Fazer inferência em frames alternados reduz bastante a carga da CPU.
INFERENCE_EVERY_N_FRAMES = 2

CONFIRMATION_FRAMES = 2
ALERT_DURATION = 2.5
ALERT_COOLDOWN = 1.0

# Sua GPU é AMD, portanto não usamos CUDA.
USE_CUDA = False


WEAPON_CLASSES = {
    "knife": "FACA",
    "faca": "FACA",

    "gun": "ARMA DE FOGO",
    "pistol": "ARMA DE FOGO",
    "firearm": "ARMA DE FOGO",

    "weapon": "ARMA",
    "arma": "ARMA",
}