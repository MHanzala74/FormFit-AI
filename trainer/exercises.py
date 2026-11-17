"""Exercise analyzers: rep counting and posture rules for squats and push-ups."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .angles import angle_from_vertical, calculate_angle
from .pose_estimator import Landmarks

MIN_VISIBILITY = 0.5


@dataclass
class Analysis:
    reps: int = 0
    stage: str = "up"
    angles: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    rep_completed: bool = False
    posture_ok: bool = True


def _best_side(lm: Landmarks, joints: List[str]) -> Optional[str]:
    """Pick the body side (left/right) whose joints are most visible."""
    best, best_score = None, 0.0
    for side in ("left", "right"):
        vis = [lm[f"{side}_{j}"][2] for j in joints]
        score = min(vis)
        if score > best_score:
            best, best_score = side, score
    return best if best_score >= MIN_VISIBILITY else None


def _pt(lm: Landmarks, side: str, joint: str):
    x, y, _ = lm[f"{side}_{joint}"]
    return (x, y)


class Exercise:
    name = "exercise"

    def __init__(self):
        self.reps = 0
        self.stage = "up"
        self._min_depth_angle = 180.0
        self._bad_form_this_rep = False

    def analyze(self, lm: Optional[Landmarks]) -> Analysis:
        raise NotImplementedError


class Squat(Exercise):
    """Side-view squat. Tracks knee angle (depth) and torso lean (back)."""

    name = "squat"
    UP_ANGLE = 160        # knee angle when standing
    DOWN_ANGLE = 105      # knee angle that counts as a full-depth squat
    MAX_TORSO_LEAN = 55   # degrees from vertical before warning about the back
    MAX_KNEE_FORWARD = 0.0  # reserved for future knee-over-toe check

    def analyze(self, lm):
        result = Analysis(reps=self.reps, stage=self.stage)
        if lm is None:
            result.warnings.append("Stand in front of the camera")
            result.posture_ok = False
            return result
        side = _best_side(lm, ["shoulder", "hip", "knee", "ankle"])
        if side is None:
            result.warnings.append("Show your full body from the side")
            result.posture_ok = False
            return result

        shoulder, hip = _pt(lm, side, "shoulder"), _pt(lm, side, "hip")
        knee, ankle = _pt(lm, side, "knee"), _pt(lm, side, "ankle")
        knee_angle = calculate_angle(hip, knee, ankle)
        lean = angle_from_vertical(shoulder, hip)
        result.angles = {"knee": knee_angle, "torso_lean": lean}

        if self.stage == "up" and knee_angle < self.UP_ANGLE - 15:
            self.stage = "down"
            self._min_depth_angle = knee_angle
            self._bad_form_this_rep = False
        elif self.stage == "down":
            self._min_depth_angle = min(self._min_depth_angle, knee_angle)
            if knee_angle > self.UP_ANGLE:
                self.stage = "up"
                if self._min_depth_angle <= self.DOWN_ANGLE:
                    self.reps += 1
                    result.rep_completed = True
                else:
                    result.warnings.append("Go lower")
                    result.posture_ok = False

        if self.stage == "down" and lean > self.MAX_TORSO_LEAN:
            result.warnings.append("Keep your back straight")
            result.posture_ok = False

        result.reps, result.stage = self.reps, self.stage
        return result


class PushUp(Exercise):
    """Side-view push-up. Tracks elbow angle (depth) and body line (hips)."""

    name = "pushup"
    UP_ANGLE = 155
    DOWN_ANGLE = 95
    MIN_BODY_LINE = 150   # shoulder-hip-ankle angle; lower means sagging/piking

    def analyze(self, lm):
        result = Analysis(reps=self.reps, stage=self.stage)
        if lm is None:
            result.warnings.append("Stand in front of the camera")
            result.posture_ok = False
            return result
        side = _best_side(lm, ["shoulder", "elbow", "wrist", "hip", "ankle"])
        if side is None:
            result.warnings.append("Show your full body from the side")
            result.posture_ok = False
            return result

        shoulder, elbow, wrist = _pt(lm, side, "shoulder"), _pt(lm, side, "elbow"), _pt(lm, side, "wrist")
        hip, ankle = _pt(lm, side, "hip"), _pt(lm, side, "ankle")
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        body_line = calculate_angle(shoulder, hip, ankle)
        result.angles = {"elbow": elbow_angle, "body_line": body_line}

        if self.stage == "up" and elbow_angle < self.UP_ANGLE - 15:
            self.stage = "down"
            self._min_depth_angle = elbow_angle
        elif self.stage == "down":
            self._min_depth_angle = min(self._min_depth_angle, elbow_angle)
            if elbow_angle > self.UP_ANGLE:
                self.stage = "up"
                if self._min_depth_angle <= self.DOWN_ANGLE:
                    self.reps += 1
                    result.rep_completed = True
                else:
                    result.warnings.append("Go lower")
                    result.posture_ok = False

        if body_line < self.MIN_BODY_LINE:
            result.warnings.append("Keep your body in a straight line")
            result.posture_ok = False

        result.reps, result.stage = self.reps, self.stage
        return result


EXERCISES = {"squat": Squat, "pushup": PushUp}


def create_exercise(name: str) -> Exercise:
    try:
        return EXERCISES[name.lower()]()
    except KeyError:
        raise ValueError(f"Unknown exercise {name!r}. Choose from: {', '.join(EXERCISES)}")
