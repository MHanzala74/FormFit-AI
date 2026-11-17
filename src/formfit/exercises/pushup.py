from __future__ import annotations

from typing import Dict, List, Optional

from formfit.core.angles import calculate_angle
from formfit.core.types import Landmarks

from .base import Exercise, side_points


def body_line_angles(shoulder, hip, ankle) -> tuple[float, float]:
    """Return (body_line, hip_sag) in degrees for a plank-like body position.

    ``body_line`` is the shoulder-hip-ankle angle (180 = perfectly straight).
    ``hip_sag`` is that deviation signed: positive when the hips drop below the
    shoulder-ankle line, negative when they pike up.
    """
    line = calculate_angle(shoulder, hip, ankle)
    dx = ankle[0] - shoulder[0]
    if dx == 0:
        return line, 0.0
    t = (hip[0] - shoulder[0]) / dx
    y_on_line = shoulder[1] + t * (ankle[1] - shoulder[1])
    sign = 1.0 if hip[1] > y_on_line else -1.0
    return line, sign * (180.0 - line)


class PushUp(Exercise):
    """Push-up, filmed from the side.

    Primary angle: elbow (shoulder-elbow-wrist). Form: straight body line.
    """

    name = "pushup"
    display_name = "Push-up"
    description = "Depth via elbow angle, core stability via shoulder-hip-ankle line."
    primary_joint = "elbow"
    joints = ("shoulder", "elbow", "wrist", "hip", "ankle")

    rest_angle = 160.0
    start_angle = 140.0
    target_angle = 95.0
    shallow_hint = "Go lower"
    MIN_BODY_LINE = 155.0

    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        p = side_points(lm, side)
        elbow = calculate_angle(p["shoulder"], p["elbow"], p["wrist"])
        line, sag = body_line_angles(p["shoulder"], p["hip"], p["ankle"])
        return {"primary": elbow, "elbow": elbow, "body_line": line, "hip_sag": sag}

    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        if angles["body_line"] >= self.MIN_BODY_LINE:
            return []
        return ["Don't let your hips sag"] if angles["hip_sag"] > 0 else ["Lower your hips"]
