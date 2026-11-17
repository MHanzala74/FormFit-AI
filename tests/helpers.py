"""Synthetic pose builders used by the tests (no camera or models needed)."""

from __future__ import annotations

import math

from formfit.core.types import LANDMARK_NAMES


def blank(visibility: float = 1.0):
    return {n: (0.0, 0.0, visibility) for n in LANDMARK_NAMES}


def _set_both(lm, joint, xy, vis=1.0):
    for side in ("left", "right"):
        lm[f"{side}_{joint}"] = (float(xy[0]), float(xy[1]), vis)


def squat_pose(knee_deg: float, lean_deg: float = 10.0):
    """Side-view pose whose hip-knee-ankle angle equals ``knee_deg``."""
    lm = blank()
    ankle = (300.0, 500.0)
    knee = (300.0, 400.0)
    a = math.radians(knee_deg)
    hip = (knee[0] + 100 * math.sin(a), knee[1] + 100 * math.cos(a))
    lean = math.radians(lean_deg)
    shoulder = (hip[0] + 100 * math.sin(lean), hip[1] - 100 * math.cos(lean))
    for joint, xy in (("ankle", ankle), ("knee", knee), ("hip", hip), ("shoulder", shoulder)):
        _set_both(lm, joint, xy)
    return lm


def elbow_pose(elbow_deg: float, arm_drift_deg: float = 0.0, torso_sway_deg: float = 0.0):
    """Arm pose (curl): shoulder-elbow-wrist angle == ``elbow_deg``."""
    lm = blank()
    shoulder = (300.0, 200.0)
    d = math.radians(arm_drift_deg)
    elbow = (shoulder[0] + 100 * math.sin(d), shoulder[1] + 100 * math.cos(d))
    # Forearm direction: rotate the elbow->shoulder direction by elbow_deg.
    base = math.atan2(shoulder[1] - elbow[1], shoulder[0] - elbow[0])
    ang = base + math.radians(elbow_deg)
    wrist = (elbow[0] + 100 * math.cos(ang), elbow[1] + 100 * math.sin(ang))
    sway = math.radians(torso_sway_deg)
    hip = (shoulder[0] - 200 * math.sin(sway), shoulder[1] + 200 * math.cos(sway))
    for joint, xy in (("shoulder", shoulder), ("elbow", elbow), ("wrist", wrist), ("hip", hip)):
        _set_both(lm, joint, xy)
    return lm


def pushup_pose(elbow_deg: float, hip_offset: float = 0.0):
    """Horizontal body, shoulder left. ``hip_offset`` px: positive = hips sag."""
    lm = blank()
    shoulder, ankle = (100.0, 300.0), (500.0, 340.0)
    hip = (300.0, 320.0 + hip_offset)
    elbow = (100.0, 380.0)
    a = math.radians(elbow_deg)
    # Upper arm points down from the shoulder; forearm rotated elbow_deg from it.
    wrist = (elbow[0] + 80 * math.sin(a), elbow[1] - 80 * math.cos(a))
    for joint, xy in (("shoulder", shoulder), ("elbow", elbow), ("wrist", wrist),
                      ("hip", hip), ("ankle", ankle)):
        _set_both(lm, joint, xy)
    return lm


def plank_pose(hip_offset: float = 0.0):
    lm = blank()
    for joint, xy in (("shoulder", (100.0, 300.0)), ("hip", (300.0, 320.0 + hip_offset)),
                      ("ankle", (500.0, 340.0)), ("elbow", (100.0, 360.0)),
                      ("wrist", (160.0, 360.0)), ("knee", (400.0, 330.0))):
        _set_both(lm, joint, xy)
    return lm


def run(exercise, angles, builder, dt: float = 0.1, **kw):
    """Feed a sequence of primary angles through an exercise; returns the analyses."""
    out, t = [], 0.0
    for a in angles:
        out.append(exercise.analyze(builder(a, **kw), t=t))
        t += dt
    return out


def rep_sequence(top: float, bottom: float, steps: int = 8):
    """top -> bottom -> top angle ramp."""
    down = [top + (bottom - top) * i / steps for i in range(steps + 1)]
    return down + down[-2::-1]
