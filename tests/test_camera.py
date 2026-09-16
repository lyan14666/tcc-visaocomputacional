import sys
import time
from pathlib import Path

import cv2

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent)
)

from init import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    WINDOW_NAME,
    CONFIDENCE,
    CONFIRMATION_FRAMES
)

from test_detector import KnifeDetector
from test_alerts import AlertSystem


def draw_detection(frame, detection, confirmed):

    x1, y1, x2, y2 = detection["box"]

    confidence = detection["confidence"]
    track_id = detection["track_id"]

    if confirmed:
        color = (0, 0, 255)
        text = "FACA CONFIRMADA"
    else:
        color = (0, 255, 255)
        text = "POSSIVEL FACA"

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        3
    )

    label = f"{text} {confidence * 100:.1f}%"

    if track_id is not None:
        label += f" | ID {track_id}"

    cv2.putText(
        frame,
        label,
        (x1, max(30, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        color,
        2,
        cv2.LINE_AA
    )


def draw_status(frame, detections, confirmed, fps, confirmation):

    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, 105),
        (15, 15, 15),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.75,
        frame,
        0.25,
        0
    )

    if confirmed:

        status = "ALERTA - FACA DETECTADA"
        color = (0, 0, 255)

    elif detections:

        status = "CONFIRMANDO DETECCAO"
        color = (0, 255, 255)

    else:

        status = "MONITORANDO"
        color = (0, 255, 0)

    cv2.putText(
        frame,
        status,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"CONF: {CONFIDENCE:.2f}",
        (140, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"FRAME: {confirmation}/{CONFIRMATION_FRAMES}",
        (280, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Q/ESC: sair",
        (20, 98),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )


def main():

    print("=" * 60)
    print("TCC - SISTEMA DE DETECCAO DE FACAS")
    print("=" * 60)

    print("[1] Inicializando detector...")

    detector = KnifeDetector()

    print("[OK] Detector carregado")

    print("[2] Inicializando alertas...")

    alerts = AlertSystem()

    print("[OK] Sistema de alertas carregado")

    print("[3] Abrindo camera...")

    cap = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_V4L2
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    cap.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    if not cap.isOpened():

        raise RuntimeError(
            "Nao foi possivel abrir a camera."
        )

    print("[OK] Camera aberta")

    print("[4] Sistema iniciado")
    print("=" * 60)

    previous_time = time.time()
    fps = 0.0

    while True:

        success, frame = cap.read()

        if not success:

            print("[ERRO] Falha ao capturar frame")

            break

        frame = cv2.flip(frame, 1)

        detections = detector.detect(frame)

        confirmed = detector.is_confirmed()

        alerts.update(
            bool(detections),
            confirmed
        )

        for detection in detections:

            draw_detection(
                frame,
                detection,
                confirmed
            )

        current_time = time.time()

        delta = current_time - previous_time

        if delta > 0:

            current_fps = 1.0 / delta

            fps = (
                fps * 0.9
                +
                current_fps * 0.1
            )

        previous_time = current_time

        draw_status(
            frame,
            detections,
            confirmed,
            fps,
            detector.confirmation
        )

        cv2.imshow(
            WINDOW_NAME,
            frame
            
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

    cap.release()

    cv2.destroyAllWindows()

    print("=" * 60)
    print("Sistema encerrado.")
    print("=" * 60)


if __name__ == "__main__":
    main()