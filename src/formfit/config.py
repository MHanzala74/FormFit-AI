"""Runtime settings shared by the CLI, pipeline and web app."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Settings:
    exercise: str = "squat"
    backend: str = "mediapipe"        # "mediapipe" | "yolo"
    smoothing: float = 0.6            # EMA alpha, 1.0 = off
    min_visibility: float = 0.5       # landmarks below this are ignored
    voice: bool = True
    mirror: bool = True               # flip webcam preview like a mirror
    show_skeleton: bool = True
    yolo_weights: str = "yolov8n-pose.pt"
    mediapipe_complexity: int = 1
