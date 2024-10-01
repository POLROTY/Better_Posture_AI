# Better_Posture_AI
Analyse your posture with python OpenCV and get notified by chickens screaming at you

## Features

- Real-time posture detection using your webcam
- Alerts you with a sound when bad posture is detected
- Cross-platform support (Windows, Mac, Linux)

---

## Prerequisites

- Python 3.7 or higher
- Webcam or built-in camera
- `chickens.mp3` sound file placed in the same directory as the script

---

## Setup Instructions

### Windows

1. **Install Python**

   Download and install Python from the [official website](https://www.python.org/downloads/windows/). Make sure to check the box that says "Add Python to PATH" during installation.

2. **Open Command Prompt**

   Press `Win + R`, type `cmd`, and press `Enter`.

3. **Install Required Libraries**

   ```bash
   pip install opencv-python mediapipe pygame

4. **Download the files**

   Save the Python script posture_alert.py and chickens.mp3 in a folder or git clone this repo.

5. **Run the Script**

   Navigate to directory and run
   ```bash
   python posture_alert.py

### Mac

1. **Install Python**

   Python 3 comes pre-installed on most Macs. If not, download it from the [official website](https://www.python.org/downloads/mac-osx/).

2. **Open Command Prompt**

   Press `Command + space`, type `Terminal`, and press `Enter`.

3. **Install Required Libraries**

   ```bash
   pip3 install opencv-python mediapipe pygame

4. **Download the files**

   Save the Python script posture_alert.py and chickens.mp3 in a folder or git clone this repo.

5. **Run the Script**

   Navigate to directory and run
   ```bash
   python3 posture_alert.py

### Linux

   You should be able to figure it out...


## How It Works

- Pose Detection: Uses Mediapipe's pose estimation to detect key body landmarks.
- Angle Calculation: Calculates the angle between your head, shoulderand hip to determine posture.
- Alert Mechanism: Plays file.mp3 when the calculated angle indicates bad posture (e.g., slouching).
- Robust to Partial Visibility: Focuses on upper-body landmarks, making it effective even when the entire body isn't visible.

---



