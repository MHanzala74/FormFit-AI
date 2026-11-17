"""MediaPipe Pose backend (33 landmarks, CPU real-time)."""

from __future__ import annotations

from typing import Optional

from formfit.core.types import LANDMARK_NAMES, Landmarks

from .base import PoseEstimator

_INDICES = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
MEDIAPIPE_INDEX = dict(zip(LANDMARK_NAMES, _INDICES))


class MediaPipePose(PoseEstimator):
    name = "mediapipe"

    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        import mediapipe as mp  # lazy: the YOLO backend works without it

        self._pose = mp.solutions.pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame_bgr) -> Optional[Landmarks]:
        import cv2

        h, w = frame_bgr.shape[:2]
        result = self._pose.process(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        if not result.pose_landmarks:
            return None
        lm = result.pose_landmarks.landmark
        return {name: (lm[i].x * w, lm[i].y * h, lm[i].visibility)
                for name, i in MEDIAPIPE_INDEX.items()}

    def close(self) -> None:
        self._pose.close()
