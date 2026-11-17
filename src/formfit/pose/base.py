"""Backend interface for pose estimators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from formfit.core.types import Landmarks


class PoseEstimator(ABC):
    """Turns a BGR frame into landmarks in pixel coordinates (or ``None``)."""

    name = "base"

    @abstractmethod
    def process(self, frame_bgr) -> Optional[Landmarks]:
        ...

    def close(self) -> None:  # pragma: no cover - optional hook
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
