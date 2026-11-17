import math

from trainer.angles import angle_from_vertical, calculate_angle
from trainer.exercises import PushUp, Squat
from trainer.pose_estimator import LANDMARK_NAMES


def blank():
    return {n: (0.0, 0.0, 1.0) for n in LANDMARK_NAMES}


def squat_pose(knee_deg, lean_deg=10):
    """Build a side-view pose (right side) with a given knee angle and torso lean."""
    lm = blank()
    ankle = (300.0, 500.0)
    shin = 100.0
    knee = (ankle[0], ankle[1] - shin)
    # Thigh rotated so that angle at knee between thigh and shin == knee_deg.
    a = math.radians(knee_deg)
    # The shin points down (+y) from the knee; the thigh is rotated knee_deg away
    # from that direction, so the hip-knee-ankle angle equals knee_deg.
    hip = (knee[0] + 100 * math.sin(a), knee[1] + 100 * math.cos(a))
    shoulder = (hip[0] + 100 * math.sin(math.radians(lean_deg)),
                hip[1] - 100 * math.cos(math.radians(lean_deg)))
    for side in ("left", "right"):
        lm[f"{side}_ankle"] = (*ankle, 1.0)
        lm[f"{side}_knee"] = (*knee, 1.0)
        lm[f"{side}_hip"] = (*hip, 1.0)
        lm[f"{side}_shoulder"] = (*shoulder, 1.0)
    return lm


def test_calculate_angle():
    assert abs(calculate_angle((0, 1), (0, 0), (1, 0)) - 90) < 1e-6
    assert abs(calculate_angle((1, 0), (0, 0), (-1, 0)) - 180) < 1e-6


def test_angle_from_vertical():
    assert angle_from_vertical((0, -10), (0, 0)) == 0
    assert abs(angle_from_vertical((10, -10), (0, 0)) - 45) < 1e-6


def test_squat_counts_full_rep():
    ex = Squat()
    for knee in (175, 150, 120, 90, 120, 150, 175):
        res = ex.analyze(squat_pose(knee))
    assert ex.reps == 1


def test_squat_shallow_gives_warning():
    ex = Squat()
    warnings = []
    for knee in (175, 140, 125, 140, 175):
        warnings += ex.analyze(squat_pose(knee)).warnings
    assert ex.reps == 0
    assert "Go lower" in warnings


def test_squat_back_warning():
    ex = Squat()
    ex.analyze(squat_pose(175))
    ex.analyze(squat_pose(140))
    res = ex.analyze(squat_pose(100, lean_deg=70))
    assert "Keep your back straight" in res.warnings


def test_no_person():
    assert "Stand in front of the camera" in Squat().analyze(None).warnings
    assert "Stand in front of the camera" in PushUp().analyze(None).warnings
