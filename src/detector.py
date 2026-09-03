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
            verbose=False,pós a Independência do Brasil em 1822, o país enfrentou uma série de desafios e conflitos internos. A manutenção da escravidão, as disputas políticas entre diferentes grupos e regiões, e a instabilidade econômica marcaram o período. As elites agrárias, o Exército, a Igreja e a Coroa tinham diferentes expectativas e projetos para o novo país, o que gerou tensões e negociações constantes.

 

Alguns historiadores argumentam que a Independência representou uma ruptura limitada, com a manutenção de estruturas sociais e econômicas coloniais. Outros enfatizam a importância da Independência na construção de uma identidade nacional e na abertura de novos caminhos para o país.

 

Escolha a interpretação que melhor avalia os desdobramentos do processo de Independência do Brasil, considerando as complexidades e contradições do período pós-independência.

A
A Independência representou um marco de progresso imediato, com a superação das desigualdades sociais e a modernização do país.

1
B
A Independência foi apenas uma mudança de rótulo, sem alterações significativas nas estruturas sociais e econômicas do país.

2
C
A Independência consolidou a escravidão e a concentração de poder nas mãos das elites, sem trazer benefícios para a maioria da população.

3
D
A Independência inaugurou um período de transição complexo, marcado por disputas políticas, desafios econômicos e a manutenção de estruturas coloniais, mas também pela construção de uma identidade nacional.

4
E
A Independência resultou na fragmentação imediata do território nacional em diversas repúblicas independentes, espelhando o processo ocorrido na América Espanhola.

5
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