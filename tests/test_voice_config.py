from formfit.config import Settings
from formfit.exercises import create_exercise
from formfit.feedback import VoiceCoach
from formfit.pose import create_estimator

import pytest


def make_coach(cooldown=4.0):
    """A coach with the queue but no speech thread, so behaviour is deterministic."""
    coach = VoiceCoach(enabled=False, cooldown=cooldown)
    coach.enabled = True
    return coach


def test_disabled_coach_is_silent():
    coach = VoiceCoach(enabled=False)
    coach.say("hello")
    assert coach._queue.empty()


def test_cooldown_suppresses_repeats_but_force_overrides():
    coach = make_coach()
    coach.say("Go lower")
    coach.say("Go lower")            # inside cooldown -> dropped
    assert coach._queue.qsize() == 1
    coach.say("Go lower", force=True)
    assert coach._queue.qsize() == 2


def test_full_queue_drops_instead_of_blocking():
    coach = make_coach(cooldown=0.0)
    for text in ("a", "b", "c", "d"):
        coach.say(text)
    assert coach._queue.qsize() == 2  # maxsize, extra messages skipped


def test_settings_defaults():
    s = Settings()
    assert s.backend == "mediapipe" and 0 < s.smoothing <= 1


def test_unknown_backend_and_exercise():
    with pytest.raises(ValueError):
        create_estimator("openpose")
    with pytest.raises(ValueError):
        create_exercise("burpee")
