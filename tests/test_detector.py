import cv2
import math
from collections import deque

from ultralytics import YOLO

from init import (
    MODEL_PATH,
    CONFIDENCE,
    IOU,
    IMAGE_SIZE,
    DEVICE,
    MIN_BOX_WIDTH,
    MIN_BOX_HEIGHT,
    MIN_BOX_AREA,
    MAX_BOX_AREA_RATIO,
    CONFIRMATION_FRAMES,
    MAX_LOST_FRAMES,
    MAX_CENTER_DISTANCE,
    SMOOTHING,
    HISTORY_SIZE,
    MAX_DETECTIONS
)


class KnifeDetector:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo nao encontrado: {MODEL_PATH}"
            )

        self.model = YOLO(str(MODEL_PATH))

        self.previous_center = None
        self.previous_box = None

        self.confirmation = 0
        self.lost_frames = 0

        self.history = deque(
            maxlen=HISTORY_SIZE
        )

        self.confidence_history = deque(
            maxlen=8
        )

        self.smoothed_confidence = 0.0

        self.last_detection = None

    def distance(self, a, b):

        if a is None or b is None:
            return float("inf")

        return math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2
        )

    def box_iou(self, a, b):

        if a is None or b is None:
            return 0.0

        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        x1 = max(ax1, bx1)
        y1 = max(ay1, by1)

        x2 = min(ax2, bx2)
        y2 = min(ay2, by2)

        width = max(0, x2 - x1)
        height = max(0, y2 - y1)

        intersection = width * height

        area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
        area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

        union = area_a + area_b - intersection

        if union <= 0:
            return 0.0

        return intersection / union

    def valid_box(
        self,
        x1,
        y1,
        x2,
        y2,
        frame_width,
        frame_height
    ):

        width = x2 - x1
        height = y2 - y1

        area = width * height

        frame_area = frame_width * frame_height

        if width < MIN_BOX_WIDTH:
            return False

        if height < MIN_BOX_HEIGHT:
            return False

        if area < MIN_BOX_AREA:
            return False

        if area > frame_area * MAX_BOX_AREA_RATIO:
            return False

        ratio = width / max(height, 1)

        if ratio > 15:
            return False

        if ratio < 0.10:
            return False

        return True

    def extract_candidates(self, results, frame):

        frame_height, frame_width = frame.shape[:2]

        candidates = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                confidence = float(box.conf[0])

                class_id = int(box.cls[0])

                if class_id != 0:
                    continue

                if confidence < CONFIDENCE:
                    continue

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                x1 = max(
                    0,
                    min(x1, frame_width - 1)
                )

                y1 = max(
                    0,
                    min(y1, frame_height - 1)
                )

                x2 = max(
                    0,
                    min(x2, frame_width - 1)
                )

                y2 = max(
                    0,
                    min(y2, frame_height - 1)
                )

                if x2 <= x1 or y2 <= y1:
                    continue

                if not self.valid_box(
                    x1,
                    y1,
                    x2,
                    y2,
                    frame_width,
                    frame_height
                ):
                    continue

                center = (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2
                )

                candidates.append(
                    {
                        "box": (x1, y1, x2, y2),
                        "center": center,
                        "confidence": confidence,
                        "area": (x2 - x1) * (y2 - y1)
                    }
                )

        candidates.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        return candidates[:MAX_DETECTIONS]

    def select_detection(self, candidates):

        if not candidates:
            return None

        if self.previous_center is None:
            return candidates[0]

        scored = []

        for candidate in candidates:

            distance = self.distance(
                candidate["center"],
                self.previous_center
            )

            iou = self.box_iou(
                candidate["box"],
                self.previous_box
            )

            proximity = max(
                0.0,
                1.0 -
                distance /
                MAX_CENTER_DISTANCE
            )

            score = (
                candidate["confidence"] * 0.55 +
                iou * 0.25 +
                proximity * 0.20
            )

            candidate["score"] = score
            candidate["distance"] = distance
            candidate["iou"] = iou

            if distance <= MAX_CENTER_DISTANCE:
                scored.append(candidate)

        if not scored:

            return candidates[0]

        scored.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return scored[0]

    def update_state(self, detection):

        if detection is None:

            self.lost_frames += 1

            if self.lost_frames > MAX_LOST_FRAMES:

                self.confirmation = 0
                self.previous_center = None
                self.previous_box = None

                self.history.clear()
                self.confidence_history.clear()

                self.smoothed_confidence = 0.0

                self.last_detection = None

            return None

        self.lost_frames = 0

        center = detection["center"]
        confidence = detection["confidence"]

        self.previous_center = center
        self.previous_box = detection["box"]

        self.history.append(center)

        self.confidence_history.append(
            confidence
        )

        average_confidence = sum(
            self.confidence_history
        ) / len(
            self.confidence_history
        )

        self.smoothed_confidence = (
            self.smoothed_confidence * SMOOTHING
            +
            average_confidence *
            (1.0 - SMOOTHING)
        )

        self.confirmation += 1

        detection["confirmed"] = (
            self.confirmation >=
            CONFIRMATION_FRAMES
        )

        detection["confidence_smoothed"] = (
            self.smoothed_confidence
        )

        detection["movement"] = (
            self.calculate_movement()
        )

        self.last_detection = detection

        return detection

    def calculate_movement(self):

        if len(self.history) < 2:
            return 0.0

        points = list(self.history)

        total = 0.0

        for i in range(1, len(points)):

            total += self.distance(
                points[i - 1],
                points[i]
            )

        return total

    def process(self, frame):

        results = self.model.predict(
            source=frame,
            conf=CONFIDENCE,
            iou=IOU,
            imgsz=IMAGE_SIZE,
            device=DEVICE,
            verbose=False,
            max_det=MAX_DETECTIONS
        )

        candidates = self.extract_candidates(
            results,
            frame
        )

        detection = self.select_detection(
            candidates
        )

        return self.update_state(
            detection
        )

    def draw(self, frame, detection):

        if detection is None:
            return frame

        x1, y1, x2, y2 = detection["box"]

        confirmed = detection.get(
            "confirmed",
            False
        )

        confidence = detection.get(
            "confidence_smoothed",
            detection["confidence"]
        )

        movement = detection.get(
            "movement",
            0
        )

        if confirmed:

            color = (0, 0, 255)

            text = (
                f"FACA {confidence:.2f}"
            )

        else:

            color = (0, 165, 255)

            text = (
                f"ANALISANDO "
                f"{self.confirmation}/"
                f"{CONFIRMATION_FRAMES}"
            )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            3
        )

        cv2.putText(
            frame,
            text,
            (x1, max(y1 - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

        cv2.putText(
            frame,
            f"Conf: {confidence:.2f}",
            (x1, min(y2 + 22, frame.shape[0] - 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )

        cv2.putText(
            frame,
            f"Mov: {movement:.1f}",
            (x1, min(y2 + 45, frame.shape[0] - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )

        points = list(self.history)

        for i in range(1, len(points)):

            cv2.line(
                frame,
                points[i - 1],
                points[i],
                color,
                2
            )

        return frame