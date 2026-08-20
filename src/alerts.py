from __future__ import annotations

import time

from dataclasses import dataclass
from threading import Lock


@dataclass
class Alert:

    active: bool = False

    message: str = ""

    camera: str = ""

    confidence: float = 0.0

    timestamp: float = 0.0

    source: str = ""


class AlertSystem:

    def __init__(
        self,
        camera_name,
        confirmation_frames=2,
        duration=2.5,
        cooldown=1.0,
    ):

        self.camera_name = camera_name

        self.confirmation_frames = max(
            1,
            confirmation_frames
        )

        self.duration = duration
        self.cooldown = cooldown

        self.counts = {}

        self.last_alert = 0.0

        self.alert = Alert()

        self.lock = Lock()

    def process(self, detections):

        current_labels = set()

        for detection in detections:

            label = detection.label

            current_labels.add(
                label
            )

            self.counts[label] = (
                self.counts.get(
                    label,
                    0
                ) + 1
            )

            if (
                self.counts[label]
                >= self.confirmation_frames
            ):

                self.trigger(
                    message=(
                        f"OBJETO DETECTADO: "
                        f"{label}"
                    ),
                    source=label,
                    confidence=detection.confidence
                )

        for label in list(
            self.counts
        ):

            if label not in current_labels:

                self.counts[label] -= 1

                if self.counts[label] <= 0:

                    del self.counts[label]

    def trigger(
        self,
        message,
        source,
        confidence,
    ):

        now = time.monotonic()

        with self.lock:

            if (
                now - self.last_alert
                < self.cooldown
            ):
                return

            self.alert = Alert(
                active=True,
                message=message,
                camera=self.camera_name,
                confidence=confidence,
                timestamp=now,
                source=source,
            )

            self.last_alert = now

    def update(self):

        with self.lock:

            if not self.alert.active:
                return

            if (
                time.monotonic()
                - self.alert.timestamp
                > self.duration
            ):

                self.alert.active = False

    def get(self):

        with self.lock:

            return Alert(
                active=self.alert.active,
                message=self.alert.message,
                camera=self.alert.camera,
                confidence=self.alert.confidence,
                timestamp=self.alert.timestamp,
                source=self.alert.source,
            )