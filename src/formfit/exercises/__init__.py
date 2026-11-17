"""Exercise registry."""

from __future__ import annotations

from typing import Dict, Type

from .base import ACTIVE, REST, Exercise
from .curl import BicepCurl
from .lunge import Lunge
from .plank import Plank
from .pushup import PushUp
from .squat import Squat

EXERCISES: Dict[str, Type[Exercise]] = {
    cls.name: cls for cls in (Squat, PushUp, Lunge, BicepCurl, Plank)
}


def create_exercise(name: str, **kwargs) -> Exercise:
    try:
        return EXERCISES[name.lower()](**kwargs)
    except KeyError:
        raise ValueError(f"Unknown exercise {name!r}. Choose from: {', '.join(EXERCISES)}") from None


__all__ = ["ACTIVE", "EXERCISES", "REST", "BicepCurl", "Exercise", "Lunge", "Plank",
           "PushUp", "Squat", "create_exercise"]
