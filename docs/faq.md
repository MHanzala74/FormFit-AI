# FAQ & troubleshooting

### The rep counter doesn't move
- Film from the **side** with your whole body visible; the analyzer shows "Show your full body from the side" otherwise.
- Make sure the lit area is even and you are 2-3 m from the camera.
- Check the angle number drawn on the joint: reps count only when it passes the target in `docs/exercises.md`.

### It says "Go lower" but I think my depth is fine
Angles are 2D, so a camera that isn't truly side-on changes the measurement. Re-film from the side, or lower
`target_angle` on the exercise class (see *Tuning* in `docs/exercises.md`).

### No voice / "[voice] disabled"
`pyttsx3` needs a system speech engine: SAPI5 on Windows, NSSpeech on macOS, `espeak` on Linux
(`sudo apt install espeak`). Use `--no-voice` to run silently.

### `ModuleNotFoundError: ultralytics`
The YOLO backend is optional: `pip install -e ".[yolo]"`. The first run downloads `yolov8n-pose.pt`.

### The skeleton is jittery or laggy
Tune `--smoothing`: lower values (e.g. 0.4) are steadier but lag more; `1.0` turns smoothing off.

### MediaPipe vs YOLOv8-Pose?
MediaPipe is lighter and fast on CPU. YOLOv8-Pose copes better with several people or unusual poses but is heavier;
a GPU helps. Both feed the same analysis code.

### Can I use it with a video from my phone?
Yes: `formfit analyze clip.mp4 -e squat -o annotated.mp4 --report report.json`.

### Is this medical or coaching advice?
No. It is a general-purpose form assistant. Stop if something hurts and consult a qualified professional.
