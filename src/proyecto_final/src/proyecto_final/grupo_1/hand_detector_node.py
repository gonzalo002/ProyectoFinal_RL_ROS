#!/usr/bin/env python3
import rospy
from mi_robot_pkg.msg import HandData
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import mediapipe as mp 
import numpy as np

def hand_detector():
    rospy.init_node('hand_detector_node', anonymous=True)
    pub = rospy.Publisher('/hand_data', HandData, queue_size=10)

    # Inicialización de MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    # Captura de video
    cap = cv2.VideoCapture(0)

    area_referencia_cerrada = 10000  # Ajustar según tu calibración

    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            rospy.logwarn("No frame captured from camera")
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        hand_data = HandData()
        hand_data.x = 0.0
        hand_data.y = 0.0
        hand_data.is_open = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]

                x_min = max(0, min(landmarks, key=lambda p: p[0])[0] - 30)
                y_min = max(0, min(landmarks, key=lambda p: p[1])[1] - 30)
                x_max = min(w, max(landmarks, key=lambda p: p[0])[0] + 30)
                y_max = min(h, max(landmarks, key=lambda p: p[1])[1] + 30)

                centro_x = (x_min + x_max) // 2
                centro_y = (y_min + y_max) // 2
                pos_x = centro_x - w // 2
                pos_y = h // 2 - centro_y

                hand_data.x = float(pos_x)
                hand_data.y = float(pos_y)

                # Determinar si la mano está abierta o cerrada
                mascara_mano = np.zeros(frame.shape[:2], dtype=np.uint8)
                hull = cv2.convexHull(np.array(landmarks))
                cv2.fillConvexPoly(mascara_mano, hull, 255)

                roi = cv2.bitwise_and(frame[y_min:y_max, x_min:x_max], frame[y_min:y_max, x_min:x_max], mask=mascara_mano[y_min:y_max, x_min:x_max])

                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    cnt = max(contours, key=cv2.contourArea)
                    area_cnt = cv2.contourArea(cnt)

                    if area_cnt < area_referencia_cerrada:
                        hand_data.is_open = False
                    else:
                        hand_data.is_open = True

                break  # Solo procesamos la primera mano detectada

        # Mostrar video en la ventana
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Presiona 'q' para cerrar la ventana
            break

        pub.publish(hand_data)
        rate.sleep()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        hand_detector()
    except rospy.ROSInterruptException:
        pass
