from datetime import datetime

import cv2


def draw_detection(
    frame,
    detection
):

    x1, y1, x2, y2 = (
        detection.box
    )

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 0, 255),
        3
    )

    label = (
        f"{detection.label} "
        f"{detection.confidence * 100:.0f}%"
    )

    (
        text_width,
        text_height
    ), _ = cv2.getTextSize(
        label,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        2
    )

    top = max(
        0,
        y1 - text_height - 12
    )

    cv2.rectangle(
        frame,
        (x1, top),
        (
            x1 + text_width + 10,
            y1
        ),
        (0, 0, 255),
        -1
    )

    cv2.putText(
        frame,
        label,
        (x1 + 5, y1 - 6),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


def draw_alert(
    frame,
    alert
):

    if not alert.active:
        return

    height, width = (
        frame.shape[:2]
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, 120),
        (0, 0, 180),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.88,
        frame,
        0.12,
        0,
        frame
    )

    cv2.putText(
        frame,
        "!!! ALERTA DE SEGURANCA !!!",
        (25, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.95,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        alert.message,
        (25, 76),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.82,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    info = (
        f"{alert.camera} | "
        f"{alert.source} | "
        f"{alert.confidence * 100:.0f}%"
    )

    cv2.putText(
        frame,
        info,
        (25, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    cv2.rectangle(
        frame,
        (3, 3),
        (width - 3, height - 3),
        (0, 0, 255),
        8
    )


def draw_interface(
    frame,
    fps,
    detections,
    camera_name
):

    height, width = (
        frame.shape[:2]
    )

    now = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    cv2.rectangle(
        frame,
        (0, height - 44),
        (width, height),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        camera_name,
        (15, height - 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        now,
        (width // 2 - 90, height - 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (width - 110, height - 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    if detections:

        cv2.putText(
            frame,
            f"DETECCOES: {len(detections)}",
            (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )