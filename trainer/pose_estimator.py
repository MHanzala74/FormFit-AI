"""Pose estimation backends (MediaPipe and YOLOv8-Pose).

Both backends return the same structure: a dict mapping a landmark name to
``(x, y, visibility)`` in pixel coordinates, or ``None`` if no person is found.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

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

# Index of each landmark in MediaPipe Pose (33 points) and COCO (17 points).
MEDIAPIPE_INDEX = dict(zip(LANDMARK_NAMES, [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]))
COCO_INDEX = dict(zip(LANDMARK_NAMES, [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

SKELETON = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
]


class PoseEstimator:
    """Interface for pose backends."""

    def process(self, frame_bgr) -> Optional[Landmarks]:
        raise NotImplementedError

    def close(self) -> None:
        pass


class MediaPipePose(PoseEstimator):
    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        import mediapipe as mp  # imported lazily so the YOLO backend works without it

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
        return {
            name: (lm[i].x * w, lm[i].y * h, lm[i].visibility)
            for name, i in MEDIAPIPE_INDEX.items()
        }

    def close(self) -> None:
        self._pose.close()


class YoloPose(PoseEstimator):
    def __init__(self, weights: str = "yolov8n-pose.pt", conf: float = 0.4):
        from ultralytics import YOLO

        self._model = YOLO(weights)
        self._conf = conf

    def process(self, frame_bgr) -> Optional[Landmarks]:
        results = self._model(frame_bgr, verbose=False, conf=self._conf)
        if not results or results[0].keypoints is None or len(results[0].keypoints) == 0:
            return None
        res = results[0]
        # Pick the person with the largest bounding box.
        boxes = res.boxes.xywh.cpu().numpy()
        best = int((boxes[:, 2] * boxes[:, 3]).argmax())
        xy = res.keypoints.xy[best].cpu().numpy()
        conf = res.keypoints.conf[best].cpu().numpy() if res.keypoints.conf is not None else None
        out: Landmarks = {}
        for name, i in COCO_INDEX.items():
            c = float(conf[i]) if conf is not None else 1.0
            out[name] = (float(xy[i][0]), float(xy[i][1]), c)
        return out


def create_estimator(backend: str) -> PoseEstimator:
    backend = backend.lower()
    if backend == "mediapipe":
        return MediaPipePose()
    if backend in ("yolo", "yolov8"):
        return YoloPose()
    raise ValueError(f"Unknown backend: {backend!r} (use 'mediapipe' or 'yolo')")


def draw_skeleton(frame, landmarks: Landmarks, min_visibility: float = 0.5) -> None:
    import cv2

    for a, b in SKELETON:
        pa, pb = landmarks[a], landmarks[b]
        if pa[2] >= min_visibility and pb[2] >= min_visibility:
            cv2.line(frame, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), (255, 200, 0), 3)
    for x, y, v in landmarks.values():
        if v >= min_visibility:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 120), -1)
