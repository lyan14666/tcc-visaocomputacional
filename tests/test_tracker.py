import cv2
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
    TRACKER_ENABLED,
    TRACKER_CONFIG,
    TRACKER_PERSIST,
    TRACKER_CONFIDENCE,
    TRACKER_IOU,
    TRACKER_MAX_DETECTIONS
)


class KnifeDetector:

    def __init__(self):

        print("================================")
        print("INICIANDO DETECTOR")
        print("================================")

        print("Carregando modelo...")

        self.model = YOLO(str(MODEL_PATH))

        print(f"Modelo: {MODEL_PATH}")
        print(f"Device: {DEVICE}")
        print(f"Confidence: {CONFIDENCE}")
        print(f"Tracker habilitado: {TRACKER_ENABLED}")

        if TRACKER_ENABLED:
            print(f"Tracker: {TRACKER_CONFIG}")
            print(f"Persistência: {TRACKER_PERSIST}")

        print("Detector iniciado.")
        print("================================")

        # -----------------------------
        # ESTADO DA DETECÇÃO
        # -----------------------------

        self.confirmation_count = 0
        self.lost_count = 0
        self.confirmed = False

        # -----------------------------
        # MOVIMENTO
        # -----------------------------

        self.last_center = None
        self.center_history = []

        # -----------------------------
        # BYTE TRACK
        # -----------------------------

        self.track_id = None

    # =========================================================
    # EXTRAIR CANDIDATOS
    # =========================================================

    def extract_candidates(self, result):

        candidates = []

        if result.boxes is None:
            return candidates

        boxes = result.boxes

        for index, box in enumerate(boxes):

            # ---------------------------------
            # CLASSE
            # ---------------------------------

            cls = int(box.cls[0])

            # Seu dataset possui apenas:
            # 0 = knife

            if cls != 0:
                continue

            # ---------------------------------
            # CONFIANÇA
            # ---------------------------------

            conf = float(box.conf[0])

            if conf < CONFIDENCE:
                continue

            # ---------------------------------
            # COORDENADAS
            # ---------------------------------

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            width = x2 - x1
            height = y2 - y1

            area = width * height

            # ---------------------------------
            # TAMANHO MÍNIMO
            # ---------------------------------

            if width < MIN_BOX_WIDTH:
                continue

            if height < MIN_BOX_HEIGHT:
                continue

            if area < MIN_BOX_AREA:
                continue

            # ---------------------------------
            # ÁREA RELATIVA DO FRAME
            # ---------------------------------

            frame_area = (
                result.orig_shape[0] *
                result.orig_shape[1]
            )

            if frame_area > 0:

                area_ratio = (
                    area /
                    frame_area
                )

                if area_ratio > MAX_BOX_AREA_RATIO:
                    continue

            # ---------------------------------
            # CENTRO
            # ---------------------------------

            center_x = (
                x1 + x2
            ) // 2

            center_y = (
                y1 + y2
            ) // 2

            # ---------------------------------
            # TRACK ID
            # ---------------------------------

            track_id = None

            if boxes.id is not None:

                ids = (
                    boxes.id
                    .int()
                    .cpu()
                    .tolist()
                )

                if index < len(ids):
                    track_id = ids[index]

            # ---------------------------------
            # CANDIDATO
            # ---------------------------------

            candidates.append({

                "box": (
                    x1,
                    y1,
                    x2,
                    y2
                ),

                "confidence": conf,

                "center": (
                    center_x,
                    center_y
                ),

                "area": area,

                "track_id": track_id

            })

        return candidates

    # =========================================================
    # ESCOLHER MELHOR DETECÇÃO
    # =========================================================

    def select_detection(self, candidates):

        if not candidates:
            return None

        # ---------------------------------
        # PRIMEIRA DETECÇÃO
        # ---------------------------------

        if self.last_center is None:

            return max(
                candidates,
                key=lambda x: x["confidence"]
            )

        # ---------------------------------
        # PROCURAR DETECÇÃO MAIS PRÓXIMA
        # ---------------------------------

        best = None
        best_score = -1

        for candidate in candidates:

            cx, cy = candidate["center"]

            distance = (
                (
                    cx -
                    self.last_center[0]
                ) ** 2 +

                (
                    cy -
                    self.last_center[1]
                ) ** 2

            ) ** 0.5

            # ---------------------------------
            # DISTÂNCIA MÁXIMA
            # ---------------------------------

            if distance > MAX_CENTER_DISTANCE:
                continue

            # ---------------------------------
            # SCORE DE PROXIMIDADE
            # ---------------------------------

            if MAX_CENTER_DISTANCE > 0:

                proximity_score = max(
                    0,
                    1 -
                    distance /
                    MAX_CENTER_DISTANCE
                )

            else:

                proximity_score = 0

            # ---------------------------------
            # SCORE FINAL
            # ---------------------------------

            score = (
                candidate["confidence"] *
                0.55
            ) + (
                proximity_score *
                0.45
            )

            if score > best_score:

                best_score = score
                best = candidate

        # ---------------------------------
        # FALLBACK
        # ---------------------------------

        if best is None:

            return max(
                candidates,
                key=lambda x: x["confidence"]
            )

        return best

    # =========================================================
    # ATUALIZAR ESTADO
    # =========================================================

    def update_state(self, detection):

        # ---------------------------------
        # NENHUMA DETECÇÃO
        # ---------------------------------

        if detection is None:

            self.lost_count += 1

            if (
                self.lost_count >=
                MAX_LOST_FRAMES
            ):

                self.confirmed = False

                self.confirmation_count = 0

                self.last_center = None

                self.center_history.clear()

                self.track_id = None

            return

        # ---------------------------------
        # DETECÇÃO ENCONTRADA
        # ---------------------------------

        self.lost_count = 0

        center = detection["center"]

        # ---------------------------------
        # SUAVIZAÇÃO
        # ---------------------------------

        if self.last_center is None:

            smoothed = center

        else:

            smoothed = (

                int(
                    self.last_center[0] *
                    SMOOTHING +

                    center[0] *
                    (1 - SMOOTHING)
                ),

                int(
                    self.last_center[1] *
                    SMOOTHING +

                    center[1] *
                    (1 - SMOOTHING)
                )

            )

        self.last_center = smoothed

        # ---------------------------------
        # HISTÓRICO
        # ---------------------------------

        self.center_history.append(
            smoothed
        )

        if (
            len(self.center_history) >
            HISTORY_SIZE
        ):

            self.center_history.pop(0)

        # ---------------------------------
        # CONFIRMAÇÃO
        # ---------------------------------

        self.confirmation_count += 1

        if (
            self.confirmation_count >=
            CONFIRMATION_FRAMES
        ):

            self.confirmed = True

    # =========================================================
    # PROCESSAR FRAME
    # =========================================================

    def process(self, frame):

        # =====================================================
        # BYTE TRACK
        # =====================================================

        if TRACKER_ENABLED:

            results = self.model.track(

                frame,

                persist=TRACKER_PERSIST,

                tracker=TRACKER_CONFIG,

                conf=TRACKER_CONFIDENCE,

                iou=TRACKER_IOU,

                imgsz=IMAGE_SIZE,

                device=DEVICE,

                max_det=TRACKER_MAX_DETECTIONS,

                verbose=False

            )

        # =====================================================
        # SOMENTE DETECÇÃO
        # =====================================================

        else:

            results = self.model.predict(

                frame,

                conf=CONFIDENCE,

                iou=IOU,

                imgsz=IMAGE_SIZE,

                device=DEVICE,

                max_det=5,

                verbose=False

            )

        # ---------------------------------
        # RESULTADO
        # ---------------------------------

        result = results[0]

        # ---------------------------------
        # EXTRAIR CANDIDATOS
        # ---------------------------------

        candidates = (
            self.extract_candidates(result)
        )

        # ---------------------------------
        # ESCOLHER MELHOR
        # ---------------------------------

        detection = (
            self.select_detection(
                candidates
            )
        )

        # ---------------------------------
        # RESET ID
        # ---------------------------------

        self.track_id = None

        # ---------------------------------
        # PEGAR ID DO BYTETRACK
        # ---------------------------------

        if detection is not None:

            self.track_id = (
                detection.get(
                    "track_id"
                )
            )

        # ---------------------------------
        # ATUALIZAR ESTADO
        # ---------------------------------

        self.update_state(
            detection
        )

        # ---------------------------------
        # RETORNO
        # ---------------------------------

        return (
            detection,
            self.confirmed,
            self.track_id
        )

    # =========================================================
    # DESENHAR NA TELA
    # =========================================================

    def draw(
        self,
        frame,
        detection,
        confirmed,
        track_id=None
    ):

        # =====================================================
        # NENHUMA FACA
        # =====================================================

        if detection is None:

            cv2.putText(

                frame,

                "NENHUMA FACA",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (0, 255, 0),

                2

            )

            return frame

        # =====================================================
        # COORDENADAS
        # =====================================================

        x1, y1, x2, y2 = (
            detection["box"]
        )

        conf = (
            detection["confidence"]
        )

        # =====================================================
        # STATUS
        # =====================================================

        if confirmed:

            status = "FACA CONFIRMADA"

        else:

            status = "CONFIRMANDO"

        # =====================================================
        # COR DA CAIXA
        # =====================================================

        color = (
            0,
            255,
            0
        )

        # =====================================================
        # CAIXA
        # =====================================================

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            color,

            2

        )

        # =====================================================
        # TEXTO
        # =====================================================

        label = (
            f"{status} "
            f"{conf:.2f}"
        )

        # =====================================================
        # TRACK ID
        # =====================================================

        if track_id is not None:

            label += (
                f" | ID {track_id}"
            )

        # =====================================================
        # DESENHAR TEXTO
        # =====================================================

        cv2.putText(

            frame,

            label,

            (
                x1,
                max(
                    y1 - 10,
                    20
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            color,

            2

        )

        # =====================================================
        # HISTÓRICO DE MOVIMENTO
        # =====================================================

        if len(
            self.center_history
        ) > 1:

            for i in range(
                1,
                len(
                    self.center_history
                )
            ):

                cv2.line(

                    frame,

                    self.center_history[
                        i - 1
                    ],

                    self.center_history[
                        i
                    ],

                    (255, 0, 0),

                    2

                )

        # =====================================================
        # RETORNO
        # =====================================================

        return frame