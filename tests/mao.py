import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def classificar_gesto(landmarks):
    # Pontas dos dedos
    dedos = [
        (8, 6),    # indicador
        (12, 10),  # médio
        (16, 14),  # anelar
        (20, 18)   # mindinho
    ]

    abertos = 0

    for ponta, articulacao in dedos:
        if landmarks[ponta].y < landmarks[articulacao].y:
            abertos += 1

    # Polegar
    if landmarks[4].x > landmarks[3].x:
        polegar = True
    else:
        polegar = False

    if abertos == 4 and polegar:
        return "MAO ABERTA"

    if abertos == 0:
        return "PUNHO FECHADO"

    if abertos == 1:
        return "1 DEDO"

    if abertos == 2:
        return "2 DEDOS"

    if abertos == 3:
        return "3 DEDOS"

    return "GESTO"


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: não consegui abrir a webcam.")
    exit()

while True:
    sucesso, frame = cap.read()

    if not sucesso:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:

            gesto = classificar_gesto(hand_landmarks.landmark)

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            cv2.putText(
                frame,
                gesto,
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("Classificador de Mao", frame)

    # ESC para sair
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()