import cv2
import mediapipe as mp
from pynput import keyboard

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Finger index map: 8=index, 12=middle, 16=ring, 20=pinky, 4=thumb
fingertip_ids = [4, 8, 12, 16, 20]

# Define "correct" finger mapping (very simplified)
finger_map = {
    'f': 'L_index',
    'j': 'R_index',
    'a': 'L_pinky',
    'semicolon': 'R_pinky'
    # extend this dictionary for all keys
}

pressed_key = None

def on_press(key):
    global pressed_key
    try:
        pressed_key = key.char
    except AttributeError:
        pressed_key = str(key)

listener = keyboard.Listener(on_press=on_press)
listener.start()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # mirror
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract fingertip y-coordinates (lower = finger closer to key)
            finger_positions = {fid: hand_landmarks.landmark[fid].y for fid in fingertip_ids}
            active_finger = min(finger_positions, key=finger_positions.get)

            if pressed_key:
                print(f"Key: {pressed_key}, Finger used: {active_finger}")
                # TODO: compare against finger_map and give feedback
                pressed_key = None

    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
