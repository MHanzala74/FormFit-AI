# Changelog

## 1.0.0

- Restructured into a `src/formfit` package (core, pose, exercises, feedback, session, ui, app)
- MediaPipe and YOLOv8-Pose backends behind a common interface
- Exercises: squat, push-up, lunge, bicep curl, plank
- Rep state machine with depth gate, tempo check and per-rep form score
- EMA landmark smoothing
- Voice coaching, HUD overlay, annotated video output
- Session reports (JSON / CSV / text)
- `formfit` CLI (`run`, `analyze`, `list`) and Streamlit web app
- Synthetic-pose tests, end-to-end pipeline test, GitHub Actions CI

## 0.1.0

- Initial prototype: squat and push-up rep counting with voice feedback
