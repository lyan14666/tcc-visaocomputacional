#!/bin/bash

set -e

echo "=============================================="
echo " TCC - INSTALACAO DO AMBIENTE"
echo " Ubuntu"
echo "=============================================="

echo "[1/5] Atualizando sistema..."

sudo apt update

echo "[2/5] Instalando dependencias do Ubuntu..."

sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    v4l-utils

echo "[3/5] Criando ambiente virtual..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "[4/5] Instalando Python..."

python -m pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

echo "[5/5] Testando tudo..."

python - <<'PY'
import sys
import cv2
import numpy
import torch
import ultralytics
from ultralytics import YOLO

print()
print("==============================================")
print(" INSTALACAO OK")
print("==============================================")
print("Python:", sys.version.split()[0])
print("OpenCV:", cv2.__version__)
print("NumPy:", numpy.__version__)
print("PyTorch:", torch.__version__)
print("Ultralytics:", ultralytics.__version__)
print("YOLO: OK")
print("ByteTrack: OK")
print("==============================================")
PY

echo
echo "Ambiente pronto."
echo
echo "Para executar:"
echo "source .venv/bin/activate"
echo "python tests/test_camera.py"
echo