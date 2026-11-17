import pytest
from helpers import elbow_pose, plank_pose, pushup_pose, rep_sequence, run, squat_pose

from formfit.core.angles import angle_from_horizontal, angle_from_vertical, calculate_angle
from formfit.exercises import EXERCISES, BicepCurl, Plank, PushUp, Squat, create_exercise


def test_geometry():
    assert calculate_angle((0, 1), (0, 0), (1, 0)) == pytest.approx(90)
    assert calculate_angle((1, 0), (0, 0), (-1, 0)) == pytest.approx(180)
    assert calculate_angle((0, 0), (0, 0), (1, 0)) == 0.0
    assert angle_from_vertical((0, -10), (0, 0)) == pytest.approx(0)
    assert angle_from_vertical((10, -10), (0, 0)) == pytest.approx(45)
    assert angle_from_horizontal((0, 0), (10, 10)) == pytest.approx(45)


def test_synthetic_pose_builders_match_requested_angles():
    lm = squat_pose(120)
    pts = {j: lm[f"right_{j}"][:2] for j in ("hip", "knee", "ankle")}
    assert calculate_angle(pts["hip"], pts["knee"], pts["ankle"]) == pytest.approx(120, abs=0.01)
    lm = elbow_pose(70)
    pts = {j: lm[f"right_{j}"][:2] for j in ("shoulder", "elbow", "wrist")}
    assert calculate_angle(pts["shoulder"], pts["elbow"], pts["wrist"]) == pytest.approx(70, abs=0.01)


def test_registry():
    assert set(EXERCISES) == {"squat", "pushup", "lunge", "curl", "plank"}
    assert isinstance(create_exercise("SQUAT"), Squat)
    with pytest.raises(ValueError):
        create_exercise("burpee")


def test_squat_counts_full_reps_and_scores_clean_form():
    ex = Squat()
    results = run(ex, rep_sequence(175, 90) * 3, squat_pose, dt=0.15)
    assert ex.reps == 3
    assert [r.rep.number for r in results if r.rep] == [1, 2, 3]
    assert all(r.score == 100 for r in ex.records)
    assert [r.announcement for r in results if r.announcement] == ["1", "2", "3"]


def test_squat_shallow_rep_is_not_counted():
    ex = Squat()
    results = run(ex, rep_sequence(175, 125), squat_pose, dt=0.15)
    assert ex.reps == 0
    assert any("Go lower" in r.warnings for r in results)


def test_squat_back_lean_lowers_score():
    ex = Squat()
    seq = rep_sequence(175, 90)
    results = []
    for i, k in enumerate(seq):
        lean = 75 if 4 <= i <= 12 else 10
        results.append(ex.analyze(squat_pose(k, lean_deg=lean), t=i * 0.15))
    assert ex.reps == 1
    assert "Keep your chest up" in ex.records[0].issues
    assert ex.records[0].score == 80


def test_fast_rep_gets_tempo_penalty():
    ex = Squat()
    run(ex, rep_sequence(175, 90), squat_pose, dt=0.02)
    assert ex.reps == 1
    assert "Slow down" in ex.records[0].issues


def test_progress_bar_tracks_depth():
    ex = Squat()
    top = ex.analyze(squat_pose(175), t=0)
    bottom = ex.analyze(squat_pose(90), t=0.2)
    assert top.progress == 0.0
    assert bottom.progress == 1.0


def test_no_person_and_low_visibility():
    ex = Squat()
    res = ex.analyze(None, t=0)
    assert not res.person_detected and "Step into the camera view" in res.warnings
    lm = squat_pose(120)
    lm = {k: (x, y, 0.1) for k, (x, y, _) in lm.items()}
    assert "Show your full body from the side" in ex.analyze(lm, t=0.1).warnings


def test_pushup_rep_and_hip_sag():
    ex = PushUp()
    results = run(ex, rep_sequence(170, 80), pushup_pose, dt=0.2)
    assert ex.reps == 1 and not any(r.warnings for r in results[:1])
    sag = PushUp().analyze(pushup_pose(170, hip_offset=60), t=0)
    assert "Don't let your hips sag" in sag.warnings
    pike = PushUp().analyze(pushup_pose(170, hip_offset=-60), t=0)
    assert "Lower your hips" in pike.warnings


def test_curl_flags_elbow_drift_and_counts():
    ex = BicepCurl()
    run(ex, rep_sequence(170, 40), elbow_pose, dt=0.2)
    assert ex.reps == 1
    ex2 = BicepCurl()
    results = run(ex2, rep_sequence(170, 40), elbow_pose, dt=0.2, arm_drift_deg=45)
    assert any("Keep your elbow by your side" in r.warnings for r in results)
    assert "Keep your elbow by your side" in ex2.records[0].issues


def test_plank_hold_timing_and_form_break():
    ex = Plank()
    results = [ex.analyze(plank_pose(), t=i * 0.5) for i in range(30)]  # 14.5 s of clean hold
    assert results[-1].hold_seconds == pytest.approx(14.5, abs=0.6)
    assert [r.announcement for r in results if r.announcement] == ["10 seconds"]
    broken = ex.analyze(plank_pose(hip_offset=80), t=15.0)
    assert "Don't let your hips sag" in broken.warnings
    assert ex.reps == 1 and ex.records[0].duration > 14
    assert ex.records[0].score == 80
    assert broken.hold_seconds == 0.0


def test_plank_short_hold_is_ignored_and_finalize_closes_open_hold():
    ex = Plank()
    for i in range(4):
        ex.analyze(plank_pose(), t=i * 0.5)
    ex.analyze(plank_pose(hip_offset=80), t=2.0)
    assert ex.reps == 0
    ex2 = Plank()
    for i in range(12):
        ex2.analyze(plank_pose(), t=i * 0.5)
    ex2.finalize(t=6.0)
    assert ex2.reps == 1
