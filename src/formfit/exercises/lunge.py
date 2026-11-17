from __future__ import annotations

from typing import Dict, List, Optional

from formfit.core.angles import angle_from_vertical, calculate_angle
from formfit.core.types import Landmarks

from .base import ACTIVE, Exercise, side_points


class Lunge(Exercise):
    """Forward/reverse lunge, filmed from the side.

    Primary angle: the more bent knee of the two legs. Form: upright torso.
    """

    name = "lunge"
    display_name = "Lunge"
    description = "Depth via the working knee, posture via torso lean."
    joints = ("shoulder", "hip", "knee", "ankle")

    rest_angle = 160.0
    start_angle = 145.0
    target_angle = 100.0
    shallow_hint = "Lunge deeper"
    MAX_TORSO_LEAN = 25.0

    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        knees = []
        for s in ("left", "right"):
            if min(lm[f"{s}_{j}"][2] for j in ("hip", "knee", "ankle")) >= self.min_visibility:
                p = side_points(lm, s)
                knees.append(calculate_angle(p["hip"], p["knee"], p["ankle"]))
        if not knees:
            return None
        p = side_points(lm, side)
        working = min(knees)
        return {
            "primary": working,
            "front_knee": working,
            "torso_lean": angle_from_vertical(p["shoulder"], p["hip"]),
        }

    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        if stage == ACTIVE and angles["torso_lean"] > self.MAX_TORSO_LEAN:
            return ["Keep your torso upright"]
        return []
