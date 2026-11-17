"""Pure-Python geometry helpers for joint angle calculation.

All points are ``(x, y)`` pairs in image coordinates (y grows downwards).
"""

from __future__ import annotations

import math
from typing import Sequence

Point = Sequence[float]


def calculate_angle(a: Point, b: Point, c: Point) -> float:
    """Interior angle in degrees at vertex ``b`` formed by a-b-c (range 0..180)."""
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    norm = math.hypot(*ba) * math.hypot(*bc)
    if norm == 0:
        return 0.0
    cos = (ba[0] * bc[0] + ba[1] * bc[1]) / norm
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def angle_from_vertical(top: Point, bottom: Point) -> float:
    """Angle between the segment ``bottom -> top`` and straight up.

    0 = perfectly upright, 90 = horizontal, 180 = pointing straight down.
    """
    dx, dy = top[0] - bottom[0], top[1] - bottom[1]
    norm = math.hypot(dx, dy)
    if norm == 0:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, -dy / norm))))


def angle_from_horizontal(a: Point, b: Point) -> float:
    """Absolute angle between segment a-b and the horizontal axis (0..90)."""
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    if dx == 0 and dy == 0:
        return 0.0
    return math.degrees(math.atan2(dy, dx))


def midpoint(a: Point, b: Point) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
