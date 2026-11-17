from __future__ import annotations

from typing import Dict, List, Optional

from formfit.core.angles import angle_from_vertical, calculate_angle
from formfit.core.types import Landmarks

from .base import ACTIVE, Exercise, side_points


class Squat(Exercise):
    """Bodyweight squat, filmed from the side.

    Primary angle: knee (hip-knee-ankle). Form: torso lean from vertical.
    """

    name = "squat"
    display_name = "Squat"
    description = "Depth via knee angle, chest position via torso lean."
    joints = ("shoulder", "hip", "knee", "ankle")

    rest_angle = 160.0
    start_angle = 145.0
    target_angle = 100.0
    shallow_hint = "Go lower"
    MAX_TORSO_LEAN = 55.0

    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        p = side_points(lm, side)
        knee = calculate_angle(p["hip"], p["knee"], p["ankle"])
        return {
            "primary": knee,
            "knee": knee,
            "torso_lean": angle_from_vertical(p["shoulder"], p["hip"]),
        }

    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        if stage == ACTIVE and angles["torso_lean"] > self.MAX_TORSO_LEAN:
            return ["Keep your chest up"]
        return []
