import cv2
import mediapipe as mp
import pyautogui
import time

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

last_click = 0
last_scroll_y = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_img)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = img.shape

            thumb = handLms.landmark[4]
            index = handLms.landmark[8]
            middle = handLms.landmark[12]

            # ====== MOUSE MOVE (index finger) ======
            x = int(index.x * w)
            y = int(index.y * h)

            pyautogui.moveTo(screen_w / w * x, screen_h / h * y)

            # ====== DISTANCE FUNCTION ======
            def dist(a, b):
                return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

            pinch = dist(thumb, index)
            middle_pinch = dist(thumb, middle)

            # ====== LEFT CLICK (PINCH) ======
            if pinch < 0.05:
                if time.time() - last_click > 0.5:
                    pyautogui.click()
                    last_click = time.time()

            # ====== RIGHT CLICK (3 FINGER PINCH) ======
            if middle_pinch < 0.05:
                if time.time() - last_click > 0.5:
                    pyautogui.rightClick()
                    last_click = time.time()

            # ====== SCROLL (FIXED VERSION) ======
            if abs(index.y - middle.y) < 0.03:

                scroll_y = index.y

                if last_scroll_y != 0:
                    diff = last_scroll_y - scroll_y

                    # deadzone biar tidak noise
                    if abs(diff) > 0.01:
                        pyautogui.scroll(int(diff * 1500))

                last_scroll_y = scroll_y

            else:
                last_scroll_y = 0

    cv2.imshow("Gesture Control Plus", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break