import os
import socket
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2


STREAM_HOST = "127.0.0.1"
STREAM_PORT = 8765
PANEL_HOST = "127.0.0.1"
PANEL_PORT = 8000

_latest_jpeg = None
_frame_lock = threading.Lock()
_php_process = None
_stream_server = None


class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/stream.mjpg":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "multipart/x-mixed-replace; boundary=frame"
        )
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            while True:
                with _frame_lock:
                    jpeg = _latest_jpeg

                if jpeg is not None:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(
                        f"Content-Length: {len(jpeg)}\r\n\r\n".encode()
                    )
                    self.wfile.write(jpeg)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()

                time.sleep(0.04)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def log_message(self, format, *args):
        pass


def publish_frame(frame):
    global _latest_jpeg

    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    )

    if success:
        with _frame_lock:
            _latest_jpeg = encoded.tobytes()


def port_is_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except OSError:
        return False


def start_panel(project_root):
    global _php_process, _stream_server

    os.environ.setdefault(
        "VIGIA_API_TOKEN",
        "vigia-dev-token-local-2026"
    )

    if not port_is_open(STREAM_HOST, STREAM_PORT):
        _stream_server = ThreadingHTTPServer(
            (STREAM_HOST, STREAM_PORT),
            StreamHandler
        )
        threading.Thread(
            target=_stream_server.serve_forever,
            daemon=True
        ).start()
        print(f"[PAINEL] Transmissao: http://{STREAM_HOST}:{STREAM_PORT}/stream.mjpg")
    else:
        print("[PAINEL] A porta da transmissao ja esta em uso.")

    if not port_is_open(PANEL_HOST, PANEL_PORT):
        env = os.environ.copy()
        _php_process = subprocess.Popen(
            [
                "php", "-S",
                f"{PANEL_HOST}:{PANEL_PORT}",
                "-t", str(Path(project_root) / "painel")
            ],
            cwd=str(project_root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=None
        )

        for _ in range(30):
            if port_is_open(PANEL_HOST, PANEL_PORT):
                break
            if _php_process.poll() is not None:
                raise RuntimeError(
                    "O servidor PHP encerrou. Verifique se o PHP esta instalado."
                )
            time.sleep(0.2)
        else:
            raise RuntimeError("O servidor PHP nao iniciou na porta 8000.")

        print("[PAINEL] Servidor PHP iniciado.")
    else:
        print("[PAINEL] Ja existe um servidor na porta 8000.")

    url = f"http://{PANEL_HOST}:{PANEL_PORT}/"
    print(f"[PAINEL] Abra: {url}")

    try:
        subprocess.Popen(
            ["xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError:
        print("[PAINEL] Abra o endereco acima manualmente.")


def stop_panel():
    global _php_process, _stream_server

    if _stream_server is not None:
        _stream_server.shutdown()
        _stream_server.server_close()
        _stream_server = None

    if _php_process is not None and _php_process.poll() is None:
        _php_process.terminate()
        try:
            _php_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _php_process.kill()
        _php_process = None
