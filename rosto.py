import cv2
import mediapipe as mp
import time

mp_face = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Erro ao abrir câmera")
    exit()

face_detection = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.7
)

pTime = 0

cv2.namedWindow("Contador de Pessoas", cv2.WINDOW_NORMAL)

while True:
    success, frame = cap.read()

    if not success:
        print("Falha ao ler câmera")
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_detection.process(rgb_frame)

    contador = 0

    if results.detections:
        contador = len(results.detections)

        for detection in results.detections:
            mp_drawing.draw_detection(frame, detection)

    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime

    cv2.putText(
        frame,
        f'Pessoas: {contador}',
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f'FPS: {int(fps)}',
        (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Contador de Pessoas", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

face_detection.close()
cap.release()
cv2.destroyAllWindows()