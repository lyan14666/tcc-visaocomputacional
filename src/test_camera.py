import cv2
from ultralytics import YOLO

MODEL = "runs/detect/training/runs/knife_test/weights/best.pt"

model = YOLO(MODEL)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Não foi possível abrir a câmera.")

# Tenta usar uma resolução adequada
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("=" * 50)
print("TCC - DETECÇÃO DE FACAS")
print("=" * 50)
print("Modelo:", MODEL)
print("Confiança mínima: 0.20")
print("Pressione Q para sair.")
print("=" * 50)

while True:

    ret, frame = cap.read()

    if not ret:
        print("Erro ao capturar imagem.")
        break

    # Espelha a câmera como uma webcam normal
    frame = cv2.flip(frame, 1)

    results = model.predict(
        source=frame,
        conf=0.20,
        iou=0.45,
        imgsz=640,
        device="cpu",
        verbose=False
    )

    result = results[0]

    # Desenha as detecções
    annotated = result.plot()

    # Quantidade de objetos detectados
    detections = len(result.boxes)

    # Mostra informação na tela
    cv2.putText(
        annotated,
        f"Deteccoes: {detections}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Se detectou alguma coisa
    if detections > 0:

        highest_conf = float(result.boxes.conf.max())

        cv2.putText(
            annotated,
            f"FACA DETECTADA - {highest_conf:.2f}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

    else:

        cv2.putText(
            annotated,
            "Nenhuma faca detectada",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

    cv2.imshow(
        "TCC - Deteccao de Facas",
        annotated
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()