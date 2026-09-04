import cv2
import time

from test_detector import KnifeDetector
from test_alerts import AlertManager

from init import (
    CAMERA_INDEX,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    CAMERA_BUFFER
)


def open_camera():

    camera = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_V4L2
    )

    if not camera.isOpened():

        camera.release()

        camera = cv2.VideoCapture(
            CAMERA_INDEX
        )

    if not camera.isOpened():

        raise RuntimeError(
            "Nao foi possivel abrir a camera."
        )

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        DISPLAY_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        DISPLAY_HEIGHT
    )

    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        CAMERA_BUFFER
    )

    return camera


def resize_frame(frame):

    height, width = frame.shape[:2]

    if width <= DISPLAY_WIDTH:
        return frame

    ratio = DISPLAY_WIDTH / width

    new_width = DISPLAY_WIDTH

    new_height = int(
        height * ratio
    )

    return cv2.resize(
        frame,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )


def main():

    detector = KnifeDetector()

    alert_manager = AlertManager()

    camera = open_camera()

    previous_time = time.time()

    fps = 0.0

    try:

        while True:

            success, frame = camera.read()

            if not success:
                continue

            frame = resize_frame(frame)

            detection = detector.process(
                frame
            )

            frame = detector.draw(
                frame,
                detection
            )

            confirmed = False

            if detection is not None:

                confirmed = detection.get(
                    "confirmed",
                    False
                )

            alert_manager.update(
                confirmed
            )

            current_time = time.time()

            elapsed = (
                current_time -
                previous_time
            )

            if elapsed > 0:

                instant_fps = (
                    1.0 / elapsed
                )

                fps = (
                    fps * 0.90 +
                    instant_fps * 0.10
                )

            previous_time = current_time

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Q = sair",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Detector de Facas",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == 27:
                break

    finally:

        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()