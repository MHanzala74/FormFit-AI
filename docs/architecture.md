# Architecture

FormFit AI is a small pipeline with strict boundaries so every stage can be tested and swapped independently.

```
frame ─► PoseEstimator ─► LandmarkSmoother ─► Exercise.analyze ─► Analysis
                                                     │               ├─► VoiceCoach
                                                     │               ├─► ui.annotate (HUD)
                                                     └─► records ───►└─► SessionSummary (JSON/CSV)
```

## Modules

| Module | Responsibility | Heavy deps? |
|---|---|---|
| `formfit.core` | `calculate_angle`, `angle_from_vertical`, `LandmarkSmoother`, shared dataclasses | none (pure Python) |
| `formfit.pose` | `PoseEstimator` interface; `MediaPipePose`, `YoloPose`; `create_estimator()` | lazy: mediapipe / ultralytics |
| `formfit.exercises` | `Exercise` base class (state machine, scoring) and the five exercises | none |
| `formfit.feedback` | `VoiceCoach` - queue + worker thread around `pyttsx3` | lazy: pyttsx3 |
| `formfit.session` | `SessionSummary`, JSON/CSV/text export | none |
| `formfit.ui` | OpenCV drawing (skeleton, angle label, HUD) | opencv |
| `formfit.pipeline` | `WorkoutPipeline`, `run_webcam`, `run_video` | opencv |
| `formfit.cli`, `formfit.app` | command line and Streamlit front ends | - |

Backends and TTS are imported lazily, so the analysis logic and its tests run without MediaPipe, YOLO or an audio device.

## Data contract

Every backend returns the same thing: `Dict[str, (x, y, visibility)]` in pixel coordinates for 13 landmarks
(`nose`, `left/right_{shoulder, elbow, wrist, hip, knee, ankle}`), or `None` if nobody is detected. MediaPipe's 33
points and COCO's 17 keypoints are both mapped onto this set, which is what makes the backends interchangeable.

## Rep state machine

All rep exercises share one *primary angle* that is large at rest and small at the peak.

```
            primary < start_angle
   ┌──────┐ ─────────────────────► ┌────────┐
   │ REST │                        │ ACTIVE │  track min(primary), collect posture issues
   └──────┘ ◄───────────────────── └────────┘
            primary > rest_angle
              │
              ├─ peak > target + tolerance  → not counted, hint ("Go lower")
              └─ otherwise                  → rep counted, score = 100 - 20 × issues
                                              (tempo < min_rep_seconds adds "Slow down")
```

Plank is time-based: a *hold* runs while the body line is straight; it is recorded when the form breaks, the person
leaves the position, or the session ends (`finalize`).

## Adding an exercise

1. Create `src/formfit/exercises/<name>.py` with a subclass of `Exercise`.
2. Set `joints`, `primary_joint`, `rest_angle`, `start_angle`, `target_angle`.
3. Implement `measure(lm, side)` (return a dict with `"primary"`) and `check_form(angles, stage)` (return warnings).
4. Register it in `formfit/exercises/__init__.py`.
5. Add a synthetic-pose test in `tests/` and a row in `docs/exercises.md`.

## Timing

`Exercise.analyze(landmarks, t)` takes an explicit timestamp. Live mode uses the wall clock; offline video analysis uses
`frame_index / fps`, so results are deterministic and independent of processing speed.
