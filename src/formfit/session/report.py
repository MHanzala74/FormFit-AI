"""Workout session summaries and export (JSON / CSV / text)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from formfit.core.types import RepRecord


@dataclass
class SessionSummary:
    exercise: str
    started_at: str
    duration_seconds: float
    frames: int
    total_reps: int
    avg_form_score: float
    best_rep: int | None = None
    worst_rep: int | None = None
    total_hold_seconds: float = 0.0
    common_issues: List[Tuple[str, int]] = field(default_factory=list)
    reps: List[RepRecord] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["common_issues"] = [{"issue": i, "count": c} for i, c in self.common_issues]
        return data

    # ------------------------------------------------------------------ export
    def save_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path

    def save_csv(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["rep", "time_s", "duration_s", "peak_angle", "score", "issues"])
            for r in self.reps:
                writer.writerow([r.number, f"{r.timestamp:.2f}", f"{r.duration:.2f}",
                                 f"{r.peak_angle:.1f}", f"{r.score:.0f}", "; ".join(r.issues)])
        return path

    def text(self) -> str:
        unit = "holds" if self.exercise == "plank" else "reps"
        lines = [
            f"FormFit AI - {self.exercise} session",
            f"  Duration     : {self.duration_seconds:.1f} s ({self.frames} frames)",
            f"  Total {unit:<6} : {self.total_reps}",
            f"  Avg form     : {self.avg_form_score:.0f}/100",
        ]
        if self.exercise == "plank":
            lines.append(f"  Time in plank: {self.total_hold_seconds:.1f} s")
        if self.best_rep is not None:
            lines.append(f"  Best / worst : #{self.best_rep} / #{self.worst_rep}")
        if self.common_issues:
            lines.append("  Top issues   : " + ", ".join(f"{i} x{c}" for i, c in self.common_issues))
        return "\n".join(lines)


def build_summary(exercise, duration_seconds: float, frames: int) -> SessionSummary:
    """Create a summary from a finished :class:`~formfit.exercises.base.Exercise`."""
    records = list(exercise.records)
    issues = Counter(i for r in records for i in r.issues)
    best = max(records, key=lambda r: r.score).number if records else None
    worst = min(records, key=lambda r: r.score).number if records else None
    return SessionSummary(
        exercise=exercise.name,
        started_at=datetime.now().isoformat(timespec="seconds"),
        duration_seconds=duration_seconds,
        frames=frames,
        total_reps=exercise.reps,
        avg_form_score=exercise.form_score,
        best_rep=best,
        worst_rep=worst,
        total_hold_seconds=float(getattr(exercise, "total_hold", 0.0)),
        common_issues=issues.most_common(3),
        reps=records,
    )
