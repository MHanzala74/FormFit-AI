from __future__ import annotations

import time
from typing import Dict, List, Optional

from formfit.core.angles import angle_from_horizontal
from formfit.core.types import Analysis, Landmarks, RepRecord

from .base import REST, Exercise, pick_side, side_points
from .pushup import body_line_angles

HOLD = "hold"


class Plank(Exercise):
    """Isometric plank hold, filmed from the side.

    Instead of reps, the exercise times continuous holds with a straight body
    line. A hold that lasts at least ``MIN_SEGMENT`` seconds is recorded when
    the form breaks or the person leaves the position.
    """

    name = "plank"
    display_name = "Plank"
    description = "Hold time while the shoulder-hip-ankle line stays straight."
    primary_joint = "hip"
    joints = ("shoulder", "hip", "ankle")

    MIN_BODY_LINE = 160.0
    MAX_TILT = 35.0          # shoulder-ankle line must be roughly horizontal
    MIN_SEGMENT = 3.0
    MILESTONE = 10           # announce every N seconds
    GOAL_SECONDS = 60.0      # progress bar target
    MAX_DT = 1.0             # ignore gaps longer than this (lost tracking)

    def reset(self) -> None:
        super().reset()
        self.hold_seconds = 0.0
        self.total_hold = 0.0
        self._last_t: Optional[float] = None
        self._seg_start = 0.0
        self._seg_issues: List[str] = []
        self._milestones = 0

    # Plank is time-based, so the rep-angle machinery is bypassed.
    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        p = side_points(lm, side)
        line, sag = body_line_angles(p["shoulder"], p["hip"], p["ankle"])
        return {
            "primary": line,
            "body_line": line,
            "hip_sag": sag,
            "tilt": angle_from_horizontal(p["shoulder"], p["ankle"]),
        }

    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        if angles["body_line"] >= self.MIN_BODY_LINE:
            return []
        return ["Don't let your hips sag"] if angles["hip_sag"] > 0 else ["Lower your hips"]

    def analyze(self, lm: Optional[Landmarks], t: Optional[float] = None) -> Analysis:
        t = time.monotonic() if t is None else t
        if self._t0 is None:
            self._t0 = t
        dt = 0.0 if self._last_t is None else min(t - self._last_t, self.MAX_DT)
        self._last_t = t
        result = Analysis(exercise=self.name, reps=self.reps, stage=self.stage,
                          form_score=self.form_score, hold_seconds=self.hold_seconds)

        side = pick_side(lm, self.joints, self.min_visibility) if lm else None
        angles = self.measure(lm, side) if side else None
        if angles is None:
            self._end_segment(t, result)
            return self._not_ready(result, "Show your full body from the side", detected=lm is not None)

        result.angles, result.side = angles, side
        warnings = self.check_form(angles, self.stage)
        in_position = angles["tilt"] <= self.MAX_TILT

        if in_position and not warnings:
            if self.stage != HOLD:
                self.stage, self._seg_start, self._seg_issues = HOLD, t - dt, []
            self.hold_seconds += dt
            self.total_hold += dt
            reached = int(self.hold_seconds // self.MILESTONE)
            if reached > self._milestones:
                self._milestones = reached
                result.announcement = f"{reached * self.MILESTONE} seconds"
        else:
            if in_position:
                self._seg_issues = warnings[:1]
            self._end_segment(t, result)
            if not in_position:
                warnings = ["Get into plank position"]

        result.warnings = warnings
        result.posture_ok = not warnings
        result.progress = min(1.0, self.hold_seconds / self.GOAL_SECONDS)
        result.hold_seconds = self.hold_seconds
        result.reps, result.stage, result.form_score = self.reps, self.stage, self.form_score
        return result

    def finalize(self, t: Optional[float] = None) -> None:
        self._end_segment(time.monotonic() if t is None else t, None)

    def _end_segment(self, t: float, result: Optional[Analysis]) -> None:
        if self.stage != HOLD:
            self.hold_seconds = 0.0
            self._milestones = 0
            return
        duration = self.hold_seconds
        issues = list(self._seg_issues)
        self.stage, self.hold_seconds, self._milestones = REST, 0.0, 0
        if duration < self.MIN_SEGMENT:
            return
        self.reps += 1
        record = RepRecord(
            number=self.reps,
            timestamp=t - (self._t0 or t),
            duration=duration,
            peak_angle=0.0,
            score=max(0.0, 100.0 - 20.0 * len(issues)),
            issues=issues,
        )
        self.records.append(record)
        if result is not None:
            result.rep = record
