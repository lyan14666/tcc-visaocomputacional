import cv2
from ultralytics import YOLO


# =========================================================
# CONFIGURAÇÕES
# =========================================================

MODEL_PATH = "runs/detect/runs/detect/knife_v2/weights/best.pt"

CONFIDENCE = 0.35
IOU = 0.45
IMAGE_SIZE = 640
DEVICE = "cpu"

WINDOW_NAME = "Teste - Deteccao de Facas"


# =========================================================
# CARREGAR MODELO
# =========================================================

print("=" * 60)
print("TESTE - DETECCAO DE FACAS")
print("=" * 60)

print("Modelo:", MODEL_PATH)
print("Confianca:", CONFIDENCE)
print("IOU:", IOU)
print("Imagem:", IMAGE_SIZE)
print("Device:", DEVICE)
print("=" * 60)

model = YOLO(MODEL_PATH)

print("Modelo carregado com sucesso.")
print("=" * 60)


# =========================================================
# PROCURAR CAMERA
# =========================================================

print("Procurando camera...")

cap = None

for camera_id in range(10):

    print(f"Tentando /dev/video{camera_id}...")

    test = cv2.VideoCapture(
        camera_id,
        cv2.CAP_V4L2
    )

    if not test.isOpened():
        test.release()
        continue

    ret, frame = test.read()

    if ret and frame is not None:

        cap = test

        print(
            f"Camera encontrada: /dev/video{camera_id}"
        )

        break

    test.release()


if cap is None:

    raise RuntimeError(
        "Nenhuma camera funcional foi encontrada."
    )


# =========================================================
# CONFIGURAR CAMERA
# =========================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


print("=" * 60)
print("Camera pronta.")
print("Pressione Q para sair.")
print("=" * 60)


# =========================================================
# LOOP
# =========================================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("Erro ao capturar imagem.")
        break


    # =====================================================
    # ESPELHAR CAMERA
    # =====================================================

    frame = cv2.flip(
        frame,
        1
    )


    # =====================================================
    # DETECÇÃO YOLO
    # =====================================================

    results = model.predict(

        source=frame,

        conf=CONFIDENCE,

        iou=IOU,

        imgsz=IMAGE_SIZE,

        device=DEVICE,

        verbose=False
    )


    result = results[0]


    # =====================================================
    # DESENHAR DETECÇÕES
    # =====================================================

    annotated = result.plot()


    # =====================================================
    # MOSTRAR CAMERA
    # =====================================================

    cv2.imshow(
        WINDOW_NAME,
        annotated
    )


    # =====================================================
    # TECLADO
    # =====================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# =========================================================
# ENCERRAR
# =========================================================

cap.release()

cv2.destroyAllWindows()

print("Teste encerrado.")