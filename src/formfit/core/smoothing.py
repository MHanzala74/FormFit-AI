"""Temporal smoothing of landmarks to reduce keypoint jitter."""

from __future__ import annotations

from typing import Optional

from .types import Landmarks


class LandmarkSmoother:
    """Exponential moving average over landmark positions.

    ``alpha`` is the weight of the newest observation: 1.0 disables smoothing,
    smaller values are smoother but add lag. Visibility is passed through
    untouched. State is reset after ``max_missing`` consecutive frames without a
    detection so a new person never inherits old positions.
    """

    def __init__(self, alpha: float = 0.6, max_missing: int = 10):
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.max_missing = max_missing
        self._state: Optional[Landmarks] = None
        self._missing = 0

    def reset(self) -> None:
        self._state = None
        self._missing = 0

    def update(self, landmarks: Optional[Landmarks]) -> Optional[Landmarks]:
        if landmarks is None:
            self._missing += 1
            if self._missing > self.max_missing:
                self._state = None
            return None
        self._missing = 0
        if self._state is None or self.alpha >= 1.0:
            self._state = dict(landmarks)
            return dict(landmarks)
        a = self.alpha
        smoothed: Landmarks = {}
        for name, (x, y, v) in landmarks.items():
            px, py, _ = self._state.get(name, (x, y, v))
            smoothed[name] = (a * x + (1 - a) * px, a * y + (1 - a) * py, v)
        self._state = smoothed
        return dict(smoothed)
