import cv2
import mediapipe as mp
import time
import numpy as np
from pynput.mouse import Button, Controller

# ================= CONFIG =================
mouse = Controller()

SCREEN_W = 1920   # ← Mude se sua tela for diferente
SCREEN_H = 1080

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# ================= CÂMERA =================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

# ================= VARIÁVEIS =================
prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
clicking = False
pTime = 0

print("🎯 Controle de Mouse iniciado (Ubuntu)")
print("👆 Mova o indicador")
print("🤏 Polegar + Indicador = Clique")
print("❌ Pressione Q para sair\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    h, w, _ = frame.shape
    frame_reduction = 80

    cv2.rectangle(frame, (frame_reduction, frame_reduction), 
                  (w - frame_reduction, h - frame_reduction), (255, 0, 255), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            landmarks = hand_landmarks.landmark

            index_x = int(landmarks[8].x * w)
            index_y = int(landmarks[8].y * h)
            thumb_x = int(landmarks[4].x * w)
            thumb_y = int(landmarks[4].y * h)

            # Mapeamento para tela
            mouse_x = np.interp(index_x, (frame_reduction, w - frame_reduction), (0, SCREEN_W))
            mouse_y = np.interp(index_y, (frame_reduction, h - frame_reduction), (0, SCREEN_H))

            # Suavização
            mouse_x = prev_x + (mouse_x - prev_x) * 0.5
            mouse_y = prev_y + (mouse_y - prev_y) * 0.5

            # ================= MOVE MOUSE (pynput) =================
            mouse.position = (int(mouse_x), int(mouse_y))

            prev_x, prev_y = mouse_x, mouse_y

            # ================= CLIQUE =================
            distance = np.hypot(index_x - thumb_x, index_y - thumb_y)

            if distance < 35:
                if not clicking:
                    mouse.press(Button.left)
                    clicking = True
                    cv2.putText(frame, "CLICK", (index_x + 30, index_y - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            else:
                if clicking:
                    mouse.release(Button.left)
                clicking = False

            # Desenho
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(frame, (index_x, index_y), 12, (0, 255, 0), -1)
            cv2.circle(frame, (thumb_x, thumb_y), 8, (255, 0, 0), -1)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Controle de Mouse - Ubuntu", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()