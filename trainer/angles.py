"""Geometry helpers for joint angle calculation."""

import math


def calculate_angle(a, b, c) -> float:
    """Angle in degrees at point ``b`` formed by points a-b-c (0..180).

    Each point is an (x, y) pair.
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    norm = math.hypot(*ba) * math.hypot(*bc)
    if norm == 0:
        return 0.0
    cos = (ba[0] * bc[0] + ba[1] * bc[1]) / norm
    cos = max(-1.0, min(1.0, cos))
    return math.degrees(math.acos(cos))


def angle_from_vertical(top, bottom) -> float:
    """Angle in degrees between the segment bottom->top and the vertical axis.

    0 means perfectly upright. Image y grows downwards, so "up" is -y.
    """
    dx = top[0] - bottom[0]
    dy = top[1] - bottom[1]
    if dx == 0 and dy == 0:
        return 0.0
    return math.degrees(math.atan2(abs(dx), -dy)) if dy < 0 else 180 - math.degrees(
        math.atan2(abs(dx), dy)
    )
