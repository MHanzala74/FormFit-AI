"""OpenCV drawing helpers: skeleton, joint angle labels and the HUD."""

from __future__ import annotations

from typing import Optional

import cv2

from formfit.core.types import SKELETON, Analysis, Landmarks

GREEN, RED, AMBER = (90, 220, 90), (70, 70, 240), (0, 190, 255)
WHITE, PANEL, BONE = (255, 255, 255), (28, 28, 28), (255, 200, 60)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _text(frame, text, org, scale, color=WHITE, thickness=2):
    cv2.putText(frame, text, org, FONT, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, org, FONT, scale, color, thickness, cv2.LINE_AA)


def _panel(frame, x0, y0, x1, y1, alpha=0.6):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x0, y0), (x1, y1), PANEL, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_skeleton(frame, landmarks: Landmarks, min_visibility: float = 0.5,
                  ok: bool = True) -> None:
    bone = BONE if ok else RED
    for a, b in SKELETON:
        pa, pb = landmarks[a], landmarks[b]
        if pa[2] >= min_visibility and pb[2] >= min_visibility:
            cv2.line(frame, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), bone, 3, cv2.LINE_AA)
    for x, y, v in landmarks.values():
        if v >= min_visibility:
            cv2.circle(frame, (int(x), int(y)), 5, GREEN, -1, cv2.LINE_AA)


def draw_primary_angle(frame, landmarks: Landmarks, analysis: Analysis, joint: str) -> None:
    """Label the tracked joint with its current angle."""
    if not analysis.side or not analysis.angles:
        return
    x, y, _ = landmarks[f"{analysis.side}_{joint}"]
    color = GREEN if analysis.posture_ok else RED
    cv2.circle(frame, (int(x), int(y)), 11, color, 2, cv2.LINE_AA)
    scale = max(frame.shape[1] / 1280, 0.5)
    _text(frame, f"{analysis.angles['primary']:.0f}", (int(x) + 14, int(y) - 10), 0.8 * scale, color)


def draw_hud(frame, analysis: Analysis, title: str, plank: bool = False) -> None:
    h, w = frame.shape[:2]
    s = max(w / 1280, 0.5)
    ok_color = GREEN if analysis.posture_ok else RED

    # Top panel: exercise, counter, stage, running form score.
    _panel(frame, 0, 0, w, int(92 * s))
    _text(frame, title.upper(), (int(18 * s), int(32 * s)), 0.85 * s, AMBER)
    if plank:
        main = f"HOLD {analysis.hold_seconds:4.1f}s"
        sub = f"holds: {analysis.reps}"
    else:
        main = f"REPS {analysis.reps}"
        sub = f"stage: {analysis.stage}"
    _text(frame, main, (int(18 * s), int(75 * s)), 1.3 * s, WHITE, 3)
    _text(frame, sub, (int(320 * s), int(75 * s)), 0.7 * s, (210, 210, 210), 2)
    score = analysis.form_score
    score_color = GREEN if score >= 80 else AMBER if score >= 60 else RED
    _text(frame, "FORM", (w - int(190 * s), int(32 * s)), 0.7 * s, (210, 210, 210), 2)
    _text(frame, f"{score:.0f}", (w - int(190 * s), int(78 * s)), 1.5 * s, score_color, 3)

    # Vertical progress bar on the right edge.
    top, bottom, x0 = int(120 * s), h - int(120 * s), w - int(46 * s)
    cv2.rectangle(frame, (x0, top), (x0 + int(24 * s), bottom), (70, 70, 70), 2)
    fill = int((bottom - top) * analysis.progress)
    cv2.rectangle(frame, (x0 + 2, bottom - fill), (x0 + int(24 * s) - 2, bottom - 2), ok_color, -1)

    # Bottom banner: status or warnings.
    if analysis.warnings:
        _panel(frame, 0, h - int(50 * s) * len(analysis.warnings) - 10, w, h, 0.7)
        for i, msg in enumerate(analysis.warnings):
            y = h - int(50 * s) * (len(analysis.warnings) - i) + int(34 * s)
            _text(frame, msg, (int(18 * s), y), 0.95 * s, RED)
    elif analysis.angles:
        _text(frame, "Good form", (int(18 * s), h - int(24 * s)), 0.95 * s, GREEN)


def annotate(frame, landmarks: Optional[Landmarks], analysis: Analysis, *, title: str,
             primary_joint: str, plank: bool = False, skeleton: bool = True,
             min_visibility: float = 0.5) -> None:
    """Draw everything onto ``frame`` in place."""
    if landmarks and skeleton:
        draw_skeleton(frame, landmarks, min_visibility, analysis.posture_ok)
        draw_primary_angle(frame, landmarks, analysis, primary_joint)
    draw_hud(frame, analysis, title, plank=plank)
