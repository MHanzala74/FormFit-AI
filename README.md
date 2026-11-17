# FormFit AI

> AI Gym Trainer & Posture Corrector

Real-time exercise tracking and posture correction using **MediaPipe Pose** (or **YOLOv8-Pose**). The app tracks joint angles during exercises like squats and push-ups and gives live voice feedback on whether your form is correct.

## Features

- Real-time pose estimation from webcam
- Joint angle calculation (knee, hip, elbow, back)
- Rep counting for squats and push-ups
- Posture checks with rules per exercise
- Voice feedback (e.g. "Go lower", "Keep your back straight")
- Switchable backend: MediaPipe or YOLOv8-Pose

## Tech Stack

- Python 3.10+
- OpenCV
- MediaPipe / Ultralytics YOLOv8-Pose
- pyttsx3 (offline text-to-speech)
- NumPy

## Project Structure

```
FormFit-AI/
├── main.py
├── requirements.txt
├── tests/
├── trainer/
│   ├── pose_estimator.py
│   ├── angles.py
│   ├── exercises.py
│   └── feedback.py
└── README.md
```

## Setup

```bash
git clone https://github.com/MHanzala74/FormFit-AI.git
cd FormFit-AI
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py --exercise squat
```

### Usage

```bash
python main.py --exercise squat                  # webcam, MediaPipe
python main.py --exercise pushup --backend yolo  # YOLOv8-Pose
python main.py --exercise squat --video clip.mp4 --no-voice
```

Film yourself from the **side** with your full body visible. Press `q` or `Esc` to quit.

### Tests

```bash
pip install pytest
pytest
```

## Roadmap

- [x] Pose estimation module
- [x] Angle calculation
- [x] Squat analysis + rep counter
- [x] Push-up analysis + rep counter
- [x] Voice feedback
- [x] YOLOv8-Pose backend
- [ ] Demo GIF

## License

MIT
