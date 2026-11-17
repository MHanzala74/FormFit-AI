from __future__ import annotations

from typing import Dict, List, Optional

from formfit.core.angles import angle_from_vertical, calculate_angle
from formfit.core.types import Landmarks

from .base import ACTIVE, Exercise, side_points


class BicepCurl(Exercise):
    """Standing dumbbell/bicep curl, one arm tracked.

    Primary angle: elbow. Form: elbow pinned to the side, no body swing.
    """

    name = "curl"
    display_name = "Bicep Curl"
    description = "Range via elbow angle, strictness via upper-arm drift and torso sway."
    primary_joint = "elbow"
    joints = ("shoulder", "elbow", "wrist", "hip")

    rest_angle = 150.0
    start_angle = 130.0
    target_angle = 55.0
    min_rep_seconds = 1.0
    shallow_hint = "Curl all the way up"
    MAX_ARM_DRIFT = 30.0
    MAX_TORSO_SWAY = 20.0

    def measure(self, lm: Landmarks, side: str) -> Optional[Dict[str, float]]:
        p = side_points(lm, side)
        elbow = calculate_angle(p["shoulder"], p["elbow"], p["wrist"])
        # Upper arm hangs straight down at 0 drift.
        drift = 180.0 - angle_from_vertical(p["elbow"], p["shoulder"])
        return {
            "primary": elbow,
            "elbow": elbow,
            "arm_drift": drift,
            "torso_sway": angle_from_vertical(p["shoulder"], p["hip"]),
        }

    def check_form(self, angles: Dict[str, float], stage: str) -> List[str]:
        if stage != ACTIVE:
            return []
        if angles["arm_drift"] > self.MAX_ARM_DRIFT:
            return ["Keep your elbow by your side"]
        if angles["torso_sway"] > self.MAX_TORSO_SWAY:
            return ["Don't swing your body"]
        return []
