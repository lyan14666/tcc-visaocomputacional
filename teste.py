import cv2

CAMERA_SOURCE = 0

camera = cv2.VideoCapture(CAMERA_SOURCE)

if not camera.isOpened():
    raise RuntimeError(
        f"Não foi possível abrir a câmera {CAMERA_SOURCE}."
    )

print("Câmera aberta.")
print("Pressione Q para sair.")

while True:

    success, frame = camera.read()

    if not success:
        print("Erro ao capturar frame.")
        break

    cv2.imshow(
        "Teste da Camera",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Câmera encerrada.")
EOF