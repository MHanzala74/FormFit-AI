"""Shared data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# name -> (x_pixels, y_pixels, visibility 0..1)
Landmarks = Dict[str, Tuple[float, float, float]]

LANDMARK_NAMES = [
    "nose",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
]

SKELETON = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
]


@dataclass
class RepRecord:
    """One completed repetition (or one plank hold segment)."""

    number: int
    timestamp: float           # seconds since the session started
    duration: float            # seconds the rep took
    peak_angle: float          # best (most extreme) primary angle reached
    score: float               # 0..100 form score
    issues: List[str] = field(default_factory=list)


@dataclass
class Analysis:
    """Result of analysing one frame."""

    exercise: str = ""
    reps: int = 0
    stage: str = "ready"
    angles: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    posture_ok: bool = True
    person_detected: bool = True
    progress: float = 0.0              # 0..1 how far through the current rep
    rep: RepRecord | None = None       # set only on the frame a rep completes
    form_score: float = 100.0          # running average over completed reps
    hold_seconds: float = 0.0          # plank only
    side: str | None = None            # which body side was analysed
    announcement: str | None = None    # positive voice event, e.g. rep count

    @property
    def rep_completed(self) -> bool:
        return self.rep is not None
