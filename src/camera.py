from __future__ import annotations

import threading
import time

import cv2


class Camera:

    def __init__(
        self,
        source=0,
        width=1280,
        height=720,
        buffer_size=1,
    ):
        self.source = source
        self.width = width
        self.height = height
        self.buffer_size = buffer_size

        self.capture = None
        self.frame = None

        self.lock = threading.Lock()

        self.running = False
        self.thread = None

    def open(self):

        if self.capture is not None:
            self.capture.release()

        self.capture = cv2.VideoCapture(
            self.source,
            cv2.CAP_V4L2
        )

        if not self.capture.isOpened():

            self.capture.release()
            self.capture = None

            return False

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        self.capture.set(
            cv2.CAP_PROP_BUFFERSIZE,
            self.buffer_size
        )

        return True

    def _update(self):

        while self.running:

            if self.capture is None:

                time.sleep(0.5)

                self.open()

                continue

            success, frame = self.capture.read()

            if not success:

                self.capture.release()
                self.capture = None

                time.sleep(0.5)

                continue

            with self.lock:
                self.frame = frame

    def start(self):

        if not self.open():

            raise RuntimeError(
                f"Não foi possível abrir "
                f"a câmera {self.source}."
            )

        self.running = True

        self.thread = threading.Thread(
            target=self._update,
            daemon=True,
            name="camera-thread"
        )

        self.thread.start()

        return self

    def read(self):

        with self.lock:

            if self.frame is None:
                return None

            return self.frame.copy()

    def stop(self):

        self.running = False

        if self.thread is not None:

            self.thread.join(
                timeout=1.5
            )

            self.thread = None

        if self.capture is not None:

            self.capture.release()
            self.capture = None