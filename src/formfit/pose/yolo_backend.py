"""Ultralytics YOLOv8-Pose backend (17 COCO keypoints)."""

from __future__ import annotations

from typing import Optional

from formfit.core.types import LANDMARK_NAMES, Landmarks

from .base import PoseEstimator

_INDICES = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
COCO_INDEX = dict(zip(LANDMARK_NAMES, _INDICES))


class YoloPose(PoseEstimator):
    name = "yolo"

    def __init__(self, weights: str = "yolov8n-pose.pt", conf: float = 0.4):
        from ultralytics import YOLO

        self._model = YOLO(weights)
        self._conf = conf

    def process(self, frame_bgr) -> Optional[Landmarks]:
        results = self._model(frame_bgr, verbose=False, conf=self._conf)
        if not results or results[0].keypoints is None or len(results[0].keypoints) == 0:
            return None
        res = results[0]
        # With several people in frame, follow the one with the largest box.
        boxes = res.boxes.xywh.cpu().numpy()
        best = int((boxes[:, 2] * boxes[:, 3]).argmax())
        xy = res.keypoints.xy[best].cpu().numpy()
        conf = res.keypoints.conf[best].cpu().numpy() if res.keypoints.conf is not None else None
        return {
            name: (float(xy[i][0]), float(xy[i][1]), float(conf[i]) if conf is not None else 1.0)
            for name, i in COCO_INDEX.items()
        }
