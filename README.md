# AI Gym Trainer & Posture Corrector

Real-time exercise tracking and posture correction using **MediaPipe Pose** (or **YOLOv8-Pose**). The app tracks joint angles during exercises like squats and push-ups and gives live voice feedback on whether your form is correct.

## Features (planned)

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
ai-gym-trainer/
├── main.py
├── requirements.txt
├── trainer/
│   ├── pose_estimator.py
│   ├── angles.py
│   ├── exercises.py
│   └── feedback.py
└── README.md
```

## Setup

```bash
git clone https://github.com/MHanzala74/ai-gym-trainer.git
cd ai-gym-trainer
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Roadmap

- [ ] Pose estimation module
- [ ] Angle calculation
- [ ] Squat analysis + rep counter
- [ ] Push-up analysis + rep counter
- [ ] Voice feedback
- [ ] YOLOv8-Pose backend
- [ ] Demo GIF

## License

MIT
