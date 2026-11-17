import json

import cv2
import numpy as np
import pytest
from helpers import rep_sequence, squat_pose

from formfit import cli
from formfit.config import Settings
from formfit.core.smoothing import LandmarkSmoother
from formfit.feedback import VoiceCoach
from formfit.pipeline import WorkoutPipeline, run_video
from formfit.pose.base import PoseEstimator


class ScriptedPose(PoseEstimator):
    """Returns a pre-scripted landmark set per frame (stands in for MediaPipe/YOLO)."""

    def __init__(self, poses):
        self.poses, self.i = poses, 0

    def process(self, frame_bgr):
        pose = self.poses[min(self.i, len(self.poses) - 1)]
        self.i += 1
        return pose


def make_video(path, frames, fps=10, size=(640, 600)):
    w, h = size
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for _ in range(frames):
        writer.write(np.zeros((h, w, 3), dtype=np.uint8))
    writer.release()


def test_smoother_blends_and_resets():
    s = LandmarkSmoother(alpha=0.5, max_missing=2)
    assert s.update({"nose": (0, 0, 1)}) == {"nose": (0, 0, 1)}
    assert s.update({"nose": (10, 20, 0.9)})["nose"] == (5.0, 10.0, 0.9)
    for _ in range(3):
        assert s.update(None) is None
    assert s.update({"nose": (100, 100, 1)})["nose"] == (100, 100, 1)  # state was reset
    with pytest.raises(ValueError):
        LandmarkSmoother(alpha=0)


def test_pipeline_process_draws_and_counts():
    poses = [squat_pose(k) for k in rep_sequence(175, 90) * 2]
    pipe = WorkoutPipeline(Settings(exercise="squat", smoothing=1.0),
                           estimator=ScriptedPose(poses), voice=VoiceCoach(enabled=False))
    frame = np.zeros((600, 640, 3), dtype=np.uint8)
    for i in range(len(poses)):
        out, analysis = pipe.process(frame.copy(), t=i * 0.15)
    assert analysis.reps == 2
    assert out.any()  # HUD pixels were drawn
    summary = pipe.finish()
    assert summary.total_reps == 2 and summary.avg_form_score == 100
    assert summary.duration_seconds == pytest.approx((len(poses) - 1) * 0.15)
    assert 0 < summary.reps[0].timestamp < summary.reps[1].timestamp


def test_run_video_end_to_end_with_report(tmp_path):
    seq = rep_sequence(175, 90) * 3
    video = tmp_path / "in.mp4"
    make_video(video, len(seq), fps=7)
    out = tmp_path / "out" / "annotated.mp4"
    summary = run_video(str(video), Settings(exercise="squat", smoothing=1.0), output=str(out),
                        estimator=ScriptedPose([squat_pose(k) for k in seq]))
    assert summary.total_reps == 3
    assert out.exists() and out.stat().st_size > 0
    summary.save_json(tmp_path / "r.json")
    summary.save_csv(tmp_path / "r.csv")
    data = json.loads((tmp_path / "r.json").read_text())
    assert data["total_reps"] == 3 and len(data["reps"]) == 3
    assert (tmp_path / "r.csv").read_text().splitlines()[0].startswith("rep,")
    assert "squat session" in summary.text()


def test_run_video_missing_file():
    with pytest.raises(FileNotFoundError):
        run_video("nope.mp4", Settings())


def test_cli_list_and_errors(capsys):
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    for name in ("squat", "pushup", "lunge", "curl", "plank"):
        assert name in out
    assert cli.main(["analyze", "missing.mp4", "--exercise", "squat"]) == 1
