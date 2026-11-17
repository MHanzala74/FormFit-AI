"""High-level workout pipeline: frames in, annotated frames + analysis out."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional, Tuple

import cv2

from formfit.config import Settings
from formfit.core.smoothing import LandmarkSmoother
from formfit.core.types import Analysis
from formfit.exercises import create_exercise
from formfit.feedback import VoiceCoach
from formfit.pose import PoseEstimator, create_estimator
from formfit.session import SessionSummary, build_summary
from formfit.ui import annotate


class WorkoutPipeline:
    """Wires pose estimation, smoothing, exercise analysis, drawing and voice together."""

    def __init__(self, settings: Settings, estimator: Optional[PoseEstimator] = None,
                 voice: Optional[VoiceCoach] = None):
        self.settings = settings
        self.estimator = estimator or self._make_estimator(settings)
        self.exercise = create_exercise(settings.exercise, min_visibility=settings.min_visibility)
        self.smoother = LandmarkSmoother(settings.smoothing)
        self.voice = voice if voice is not None else VoiceCoach(enabled=settings.voice)
        self.frames = 0
        self._t_first: Optional[float] = None
        self._t_last = 0.0

    @staticmethod
    def _make_estimator(settings: Settings) -> PoseEstimator:
        if settings.backend == "yolo":
            return create_estimator("yolo", weights=settings.yolo_weights)
        return create_estimator("mediapipe", model_complexity=settings.mediapipe_complexity)

    def process(self, frame, t: Optional[float] = None, draw: bool = True) -> Tuple[object, Analysis]:
        """Analyse one BGR frame. ``t`` is the timestamp in seconds (defaults to wall clock)."""
        t = time.monotonic() if t is None else t
        if self._t_first is None:
            self._t_first = t
        self._t_last = t
        self.frames += 1

        landmarks = self.smoother.update(self.estimator.process(frame))
        analysis = self.exercise.analyze(landmarks, t=t)

        if analysis.announcement:
            self.voice.say(analysis.announcement, force=True)
        for msg in analysis.warnings:
            self.voice.say(msg)
        if draw:
            annotate(frame, landmarks, analysis, title=self.exercise.display_name,
                     primary_joint=self.exercise.primary_joint,
                     plank=self.exercise.name == "plank",
                     skeleton=self.settings.show_skeleton,
                     min_visibility=self.settings.min_visibility)
        return frame, analysis

    def finish(self) -> SessionSummary:
        self.exercise.finalize(self._t_last)
        duration = self._t_last - (self._t_first or self._t_last)
        return build_summary(self.exercise, duration, self.frames)

    def close(self) -> None:
        self.estimator.close()
        self.voice.close()


def run_webcam(settings: Settings, camera: int = 0, record: Optional[str] = None,
               window: str = "FormFit AI") -> SessionSummary:
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {camera}")
    pipeline = WorkoutPipeline(settings)
    writer = None
    pipeline.voice.say(f"Starting {pipeline.exercise.display_name}. Get into position.", force=True)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if settings.mirror:
                frame = cv2.flip(frame, 1)
            frame, _ = pipeline.process(frame)
            if record:
                if writer is None:
                    h, w = frame.shape[:2]
                    writer = cv2.VideoWriter(record, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
                writer.write(frame)
            cv2.imshow(window, frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        summary = pipeline.finish()
        pipeline.voice.say(f"Workout finished. {summary.total_reps} reps.", force=True)
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        pipeline.close()
    return summary


def run_video(path: str, settings: Settings, output: Optional[str] = None, show: bool = False,
              progress: Optional[Callable[[int, int], None]] = None,
              estimator: Optional[PoseEstimator] = None) -> SessionSummary:
    """Analyse a video file offline. Timestamps come from the video's own frame rate."""
    if not Path(path).is_file():
        raise FileNotFoundError(path)
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    settings.voice = False
    pipeline = WorkoutPipeline(settings, estimator=estimator, voice=VoiceCoach(enabled=False))
    writer = None
    index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame, _ = pipeline.process(frame, t=index / fps, draw=bool(output or show))
            if output:
                if writer is None:
                    h, w = frame.shape[:2]
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    writer = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                writer.write(frame)
            if show:
                cv2.imshow("FormFit AI", frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
            index += 1
            if progress:
                progress(index, total)
    finally:
        summary = pipeline.finish()
        cap.release()
        if writer:
            writer.release()
        if show:
            cv2.destroyAllWindows()
        pipeline.close()
    return summary
