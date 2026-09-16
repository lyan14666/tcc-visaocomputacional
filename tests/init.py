from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "runs/detect/runs/detect/knife_v3_negativos/weights/best.pt"

CAMERA_INDEX = 0

CONFIDENCE = 0.35
IOU = 0.45
IMAGE_SIZE = 640
DEVICE = "cpu"

TRACKER = "bytetrack.yaml"
TRACKER_PERSIST = True

MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 10
MIN_BOX_AREA = 300

MAX_BOX_AREA_RATIO = 0.80

CONFIRMATION_FRAMES = 4
LOST_FRAMES = 8

MAX_DETECTIONS = 5

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

WINDOW_NAME = "TCC - Deteccao de Facas"

ALERT_COOLDOWN = 2.0