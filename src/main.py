from __future__ import annotations

import time

import cv2

from .alerts import AlertSystem
from .camera import Camera
from .config import (
    ALERT_COOLDOWN,
    ALERT_DURATION,
    CAMERA_BUFFER_SIZE,
    CAMERA_NAME,
    CAMERA_SOURCE,
    CONFIRMATION_FRAMES,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    INFERENCE_EVERY_N_FRAMES,
    IOU_THRESHOLD,
    MODEL_PATH,
    USE_CUDA,
    WEAPON_CLASSES,
    WEAPON_CONFIDENCE,
    YOLO_IMAGE_SIZE,
)
from .detector import WeaponDetector
from .interface import (
    draw_alert,
    draw_detection,
    draw_interface,
)


def choose_device():

    if USE_CUDA:

        try:

            import torch

            if torch.cuda.is_available():
                return "cuda:0"

        except Exception:
            pass

    return "cpu"


def main():

    print("=" * 60)
    print("TCC - VISAO COMPUTACIONAL")
    print("=" * 60)

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"\nModelo não encontrado:\n"
            f"{MODEL_PATH}\n\n"
            f"Coloque o arquivo weapons.pt em:\n"
            f"models/weapons.pt"
        )

    device = choose_device()

    print(
        f"[INFO] Modelo: {MODEL_PATH}"
    )

    print(
        f"[INFO] Dispositivo: {device}"
    )

    print(
        f"[INFO] Câmera: {CAMERA_NAME}"
    )

    detector = WeaponDetector(
        model_path=MODEL_PATH,
        class_map=WEAPON_CLASSES,
        image_size=YOLO_IMAGE_SIZE,
        confidence=WEAPON_CONFIDENCE,
        iou=IOU_THRESHOLD,
        device=device,
    )

    alerts = AlertSystem(
        camera_name=CAMERA_NAME,
        confirmation_frames=CONFIRMATION_FRAMES,
        duration=ALERT_DURATION,
        cooldown=ALERT_COOLDOWN,
    )

    camera = Camera(
        source=CAMERA_SOURCE,
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        buffer_size=CAMERA_BUFFER_SIZE,
    )

    camera.start()

    window_name = CAMERA_NAME

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL
    )

    fps = 0.0

    fps_frames = 0

    fps_timer = (
        time.monotonic()
    )

    frame_counter = 0

    detections = []

    print(
        "[INFO] Sistema iniciado."
    )

    print(
        "[INFO] Q = sair"
    )

    print(
        "[INFO] F = tela cheia"
    )

    print(
        "[INFO] N = janela normal"
    )

    try:

        while True:

            frame = camera.read()

            if frame is None:

                time.sleep(
                    0.005
                )

                continue

            frame_counter += 1

            if (
                frame_counter
                % INFERENCE_EVERY_N_FRAMES
                == 0
            ):

                detections = (
                    detector.detect(
                        frame
                    )
                )

            for detection in detections:

                draw_detection(
                    frame,
                    detection
                )

            alerts.process(
                detections
            )

            alerts.update()

            current_alert = (
                alerts.get()
            )

            draw_alert(
                frame,
                current_alert
            )

            fps_frames += 1

            elapsed = (
                time.monotonic()
                - fps_timer
            )

            if elapsed >= 1.0:

                fps = (
                    fps_frames
                    / elapsed
                )

                fps_frames = 0

                fps_timer = (
                    time.monotonic()
                )

            draw_interface(
                frame,
                fps,
                detections,
                CAMERA_NAME
            )

            cv2.imshow(
                window_name,
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):
                break

            if key == ord("f"):

                cv2.setWindowProperty(
                    window_name,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_FULLSCREEN
                )

            if key == ord("n"):

                cv2.setWindowProperty(
                    window_name,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_NORMAL
                )

    finally:

        camera.stop()

        cv2.destroyAllWindows()

        print(
            "[INFO] Sistema encerrado."
        )


if __name__ == "__main__":
    main()