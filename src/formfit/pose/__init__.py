from .base import PoseEstimator

BACKENDS = ("mediapipe", "yolo")


def create_estimator(backend: str = "mediapipe", **kwargs) -> PoseEstimator:
    """Instantiate a pose backend by name. Heavy imports happen lazily here."""
    backend = backend.lower()
    if backend == "mediapipe":
        from .mediapipe_backend import MediaPipePose

        return MediaPipePose(**kwargs)
    if backend in ("yolo", "yolov8"):
        from .yolo_backend import YoloPose

        return YoloPose(**kwargs)
    raise ValueError(f"Unknown backend {backend!r}. Choose from: {', '.join(BACKENDS)}")


__all__ = ["BACKENDS", "PoseEstimator", "create_estimator"]
