from ultralytics import YOLO

from init import (
    MODEL_PATH,
    CONFIDENCE,
    IOU,
    IMAGE_SIZE,
    DEVICE,
    TRACKER,
    TRACKER_PERSIST,
    MIN_BOX_WIDTH,
    MIN_BOX_HEIGHT,
    MIN_BOX_AREA,
    MAX_BOX_AREA_RATIO,
    CONFIRMATION_FRAMES,
    LOST_FRAMES,
    MAX_DETECTIONS
)


class KnifeDetector:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo nao encontrado: {MODEL_PATH}"
            )

        print(f"Modelo: {MODEL_PATH}")
        print(f"Confianca: {CONFIDENCE}")
        print(f"IOU: {IOU}")
        print(f"Imagem: {IMAGE_SIZE}")
        print(f"Device: {DEVICE}")
        print(f"Tracker: {TRACKER}")

        self.model = YOLO(str(MODEL_PATH))

        self.confirmation = 0
        self.lost = 0
        self.confirmed = False

    def detect(self, frame):

        results = self.model.track(
            frame,
            persist=TRACKER_PERSIST,
            tracker=TRACKER,
            conf=CONFIDENCE,
            iou=IOU,
            imgsz=IMAGE_SIZE,
            device=DEVICE,
            max_det=MAX_DETECTIONS,
            verbose=False
        )

        result = results[0]

        detections = []

        if result.boxes is None:
            self._lost()
            return detections

        boxes = result.boxes

        ids = None

        if boxes.id is not None:
            ids = boxes.id.int().cpu().tolist()

        for index, box in enumerate(boxes):

            cls = int(box.cls[0])

            if cls != 0:
                continue

            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            width = x2 - x1
            height = y2 - y1
            area = width * height

            if width < MIN_BOX_WIDTH:
                continue

            if height < MIN_BOX_HEIGHT:
                continue

            if area < MIN_BOX_AREA:
                continue

            frame_area = frame.shape[0] * frame.shape[1]

            if frame_area > 0:
                ratio = area / frame_area

                if ratio > MAX_BOX_AREA_RATIO:
                    continue

            track_id = None

            if ids is not None and index < len(ids):
                track_id = ids[index]

            detections.append({
                "box": (x1, y1, x2, y2),
                "confidence": confidence,
                "track_id": track_id,
                "class_id": cls
            })

        if detections:
            self.confirmation += 1
            self.lost = 0

            if self.confirmation >= CONFIRMATION_FRAMES:
                self.confirmed = True

        else:
            self._lost()

        return detections

    def _lost(self):

        self.lost += 1

        if self.lost >= LOST_FRAMES:
            self.confirmation = 0
            self.confirmed = False

    def is_confirmed(self):

        return self.confirmed

    def reset(self):

        self.confirmation = 0
        self.lost = 0
        self.confirmed = False