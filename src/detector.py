from __future__ import annotations

from dataclasses import dataclass

from ultralytics import YOLO


@dataclass(frozen=True)
class Detection:

    label: str
    confidence: float
    box: tuple[int, int, int, int]


class WeaponDetector:

    def __init__(
        self,
        model_path,
        class_map,
        image_size=640,
        confidence=0.45,
        iou=0.45,
        device="cpu",
    ):

        self.model = YOLO(
            str(model_path)
        )

        self.class_map = {
            str(key).lower().strip(): value
            for key, value in class_map.items()
        }

        self.image_size = image_size
        self.confidence = confidence
        self.iou = iou
        self.device = device

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            imgsz=self.image_size,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            verbose=False,
        )

        if not results:
            return []

        result = results[0]

        if result.boxes is None:
            return []

        if len(result.boxes) == 0:
            return []

        detections = []

        for box in result.boxes:

            confidence = float(
                box.conf[0]
            )

            class_id = int(
                box.cls[0]
            )

            class_name = str(
                result.names[class_id]
            ).lower().strip()

            if class_name not in self.class_map:
                continue

            coordinates = (
                box.xyxy[0]
                .cpu()
                .tolist()
            )

            x1, y1, x2, y2 = map(
                int,
                coordinates
            )

            detections.append(
                Detection(
                    label=self.class_map[
                        class_name
                    ],
                    confidence=confidence,
                    box=(x1, y1, x2, y2),
                )
            )

        return detections