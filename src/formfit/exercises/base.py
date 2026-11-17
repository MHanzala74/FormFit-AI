"""Exercise framework: rep state machine, depth/tempo checks and form scoring.

Every rep-based exercise is described by a single *primary angle* that is large
at rest and small at the peak of the movement (knee for squats, elbow for
push-ups and curls, ...). Subclasses only provide the geometry
(:meth:`measure`) and the posture rules (:meth:`check_form`); everything else
lives here so new exercises are a few dozen lines.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Sequence, Tuple

from formfit.core.types import Analysis, Landmarks, RepRecord

Point = Tuple[float, float]

REST, ACTIVE = "rest", "active"


def pick_side(lm: Landmarks, joints: Sequence[str], min_visibility: float) -> Optional[str]:
    """Return the body side ("left"/"right") whose required joints are most visible."""
    best, best_score = None, 0.0
    for side in ("left", "right"):
        score = min(lm[f"{side}_{j}"][2] for j in joints)
        if score > best_score:
            best, best_score = side, score
    return best if best_score >= min_visibility else None


def side_points(lm: Landmarks, side: str) -> Dict[str, Point]:
    """Joint name -> (x, y) for one body side, e.g. ``pts["knee"]``."""
    out: Dict[str, Point] = {}
    for joint in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle"):
        x, y, _ = lm[f"{side}_{joint}"]
        out[joint] = (x, y)
    return out


class Exercise(ABC):
    name = "exercise"
    display_name = "Exercise"
    description = ""
    joints: Sequence[str] = ()          # joints that must be visible on one side

    rest_angle = 160.0                  # primary angle at rest; returning above it ends a rep
    start_angle = 140.0                 # dropping below this starts a rep
    target_angle = 100.0                # peak angle needed for the rep to count
    tolerance = 5.0                     # degrees of slack on the target
    min_rep_seconds = 0.8               # faster reps get a "Slow down" note
    shallow_hint = "Go lower"

    def __init__(self, min_visibility: float = 0.5):
        self.min_visibility = min_visibility
        self.reset()

    # ------------------------------------------------------------------ state
    def reset(self) -> None:
        self.reps = 0
        self.stage = REST
        self.records: List[RepRecord] = []
        self._t0: Optional[float] = None
        self._rep_start = 0.0
        self._peak = 180.0
        self._rep_issues: List[str] = []

    @property
    def form_score(self) -> float:
        if not self.records:
            return 100.0
        return sum(r.score for r in self.records) / len(self.records)

    # ------------------------------------------------------------ subclass API
    @abstractmethod
    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        """Return a dict of angles that includes the key ``"primary"``."""

    @abstractmethod
    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        """Return posture warnings for the current frame."""

    # ----------------------------------------------------------------- analyse
    def analyze(self, lm: Optional[Landmarks], t: Optional[float] = None) -> Analysis:
        t = time.monotonic() if t is None else t
        if self._t0 is None:
            self._t0 = t
        result = Analysis(exercise=self.name, reps=self.reps, stage=self.stage,
                          form_score=self.form_score)

        if lm is None:
            return self._not_ready(result, "Step into the camera view", detected=False)
        side = pick_side(lm, self.joints, self.min_visibility)
        if side is None:
            return self._not_ready(result, "Show your full body from the side")
        angles = self.measure(lm, side)
        if angles is None:
            return self._not_ready(result, "Show your full body from the side")

        primary = angles["primary"]
        result.angles, result.side = angles, side
        span = max(self.rest_angle - self.target_angle, 1.0)
        result.progress = min(1.0, max(0.0, (self.rest_angle - primary) / span))

        self._update_state(primary, t, result)
        warnings = self.check_form(angles, self.stage)
        if self.stage == ACTIVE:
            for w in warnings:
                if w not in self._rep_issues:
                    self._rep_issues.append(w)
        result.warnings.extend(warnings)
        result.posture_ok = not result.warnings
        result.reps, result.stage, result.form_score = self.reps, self.stage, self.form_score
        return result

    def finalize(self, t: Optional[float] = None) -> None:
        """Close any open segment at the end of a session (used by timed exercises)."""

    def _not_ready(self, result: Analysis, message: str, detected: bool = True) -> Analysis:
        result.person_detected = detected
        result.warnings.append(message)
        result.posture_ok = False
        return result

    def _update_state(self, primary: float, t: float, result: Analysis) -> None:
        if self.stage == REST:
            if primary < self.start_angle:
                self.stage = ACTIVE
                self._rep_start = t
                self._peak = primary
                self._rep_issues = []
            return

        self._peak = min(self._peak, primary)
        if primary <= self.rest_angle:
            return

        # Back at rest: decide whether the rep counts.
        self.stage = REST
        if self._peak > self.target_angle + self.tolerance:
            result.warnings.append(self.shallow_hint)
            return
        duration = t - self._rep_start
        issues = list(self._rep_issues)
        if duration < self.min_rep_seconds:
            issues.append("Slow down")
            result.warnings.append("Slow down")
        self.reps += 1
        record = RepRecord(
            number=self.reps,
            timestamp=t - (self._t0 or t),
            duration=duration,
            peak_angle=self._peak,
            score=max(0.0, 100.0 - 20.0 * len(issues)),
            issues=issues,
        )
        self.records.append(record)
        result.rep = record
        result.announcement = str(self.reps)
