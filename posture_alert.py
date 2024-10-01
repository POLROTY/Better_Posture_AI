import cv2
import mediapipe as mp
import numpy as np
import time
from playsound import playsound
import os
from pathlib import Path  # Use pathlib for cross-platform paths

# Initialize MediaPipe Pose and webcam
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Change this to a different number if you have multiple cameras
# (0) usualy the main camera (1) if you have a second camera plugged in or REAR/FRONT cams
cap = cv2.VideoCapture(0)

# Initialize calibration variables
calibration_frames = 0
calibration_shoulder_angles = []
calibration_neck_angles = []
is_calibrated = False

# Initialize alert variables
alert_cooldown = 5  # seconds
last_alert_time = 0

# Define relative path for the sound file
current_dir = Path(__file__).parent  # Get the directory where this script is located
sound_file = current_dir / 'chickens.mp3'  # Replace with the correct file name

# Check if the sound file exists to avoid errors
if not sound_file.exists():
    raise FileNotFoundError(f"Sound file not found: {sound_file}")



# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)  # First point (e.g., ear)
    b = np.array(b)  # Mid point (e.g., shoulder)
    c = np.array(c)  # Reference point (e.g., horizontal line from shoulder)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Function to draw angle on the frame
def draw_angle(image, a, b, c, angle, color):
    cv2.line(image, a, b, color, 2)
    cv2.line(image, b, c, color, 2)
    cv2.circle(image, a, 5, color, -1)
    cv2.circle(image, b, 5, color, -1)
    cv2.circle(image, c, 5, color, -1)
    cv2.putText(image, f"{int(angle)}°", b, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # STEP 2: Pose Detection
        # Extract key body landmarks
        left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                         int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
        right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                          int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
        left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                    int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
        right_ear = (int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                     int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))

        # STEP 3: Angle Calculation
        # Calculate shoulder angle (line between shoulders vs. horizontal)
        shoulder_midpoint = ((left_shoulder[0] + right_shoulder[0]) // 2, (left_shoulder[1] + right_shoulder[1]) // 2)
        horizontal_point = (shoulder_midpoint[0] + 100, shoulder_midpoint[1])  # Point to the right on the horizontal line
        shoulder_angle = calculate_angle(left_shoulder, shoulder_midpoint, horizontal_point)

        # Calculate neck angle (ear-shoulder vs. vertical)
        vertical_point = (left_shoulder[0], left_shoulder[1] - 100)  # Point above the shoulder
        neck_angle = calculate_angle(left_ear, left_shoulder, vertical_point)

        # STEP 1: Calibration
        if not is_calibrated and calibration_frames < 30:
            calibration_shoulder_angles.append(shoulder_angle)
            calibration_neck_angles.append(neck_angle)
            calibration_frames += 1
            cv2.putText(frame, f"Calibrating... {calibration_frames}/30", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        elif not is_calibrated:
            shoulder_threshold = np.mean(calibration_shoulder_angles) + 5  # Adjust as needed
            neck_threshold = np.mean(calibration_neck_angles) - 5  # Adjust as needed
            is_calibrated = True
            print(f"Calibration complete. Shoulder threshold: {shoulder_threshold:.1f}, Neck threshold: {neck_threshold:.1f}")

        # Draw skeleton and angles
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        draw_angle(frame, left_shoulder, shoulder_midpoint, horizontal_point, shoulder_angle, (255, 0, 0))
        draw_angle(frame, left_ear, left_shoulder, vertical_point, neck_angle, (0, 255, 0))

        # STEP 4: Feedback
        if is_calibrated:
            current_time = time.time()
            if shoulder_angle > shoulder_threshold or neck_angle < neck_threshold:
                status = "Poor Posture"
                color = (0, 0, 255)  # Red
                if current_time - last_alert_time > alert_cooldown:
                    print("Poor posture detected! Please adjust your posture.")
                    if os.path.exists(sound_file):
                        playsound(sound_file)
                    last_alert_time = current_time
            else:
                status = "Good Posture"
                color = (0, 255, 0)  # Green

            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Shoulder Angle: {shoulder_angle:.1f}/{shoulder_threshold:.1f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Neck Angle: {neck_angle:.1f}/{neck_threshold:.1f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    else:
        cv2.putText(frame, "No person detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Posture Corrector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
