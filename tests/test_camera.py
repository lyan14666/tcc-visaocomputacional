import sys
import subprocess
import time
import json
import os
import urllib.request
from pathlib import Path


def send_alert_to_panel(detections):
    token = os.environ.get("VIGIA_API_TOKEN", "")

    if not token:
        print("[PAINEL] VIGIA_API_TOKEN nao configurado.")
        return

    if not detections:
        return

    detection = max(
        detections,
        key=lambda item: item.get("confidence", 0)
    )

    track_id = detection.get("track_id")
    if not isinstance(track_id, int):
        track_id = None

    payload = {
        "camera": "CAMERA_01",
        "confianca": float(detection["confidence"]),
        "track_id": track_id
    }

    request = urllib.request.Request(
        "http://127.0.0.1:8000/api/evento.php",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Vigia-Token": token
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            print("[PAINEL] Evento registrado:", response.read().decode("utf-8"))
    except Exception as error:
        print(f"[PAINEL] Nao foi possivel registrar o evento: {error}")



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

from panel_stream import start_panel, publish_frame, stop_panel

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
    project_root = Path(__file__).resolve().parents[1]
    os.environ.setdefault('VIGIA_API_TOKEN', 'vigia-dev-token-local-2026')
    start_panel(project_root)

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

        alert_triggered = alerts.update(
            bool(detections),
            confirmed
        )

        if alert_triggered:
            subprocess.Popen(
                ["aplay", "-q", str(project_root / "sounds" / "alerta.wav")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            send_alert_to_panel(detections)

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

        publish_frame(frame)
    cap.release()

    cv2.destroyAllWindows()
    stop_panel()

    print("=" * 60)
    print("Sistema encerrado.")
    print("=" * 60)


if __name__ == "__main__":
    main()