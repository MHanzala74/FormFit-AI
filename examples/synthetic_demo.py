"""Camera-free demo: a simulated skeleton performs squats through the real pipeline.

It exercises pose smoothing -> angle analysis -> rep counting -> HUD -> report, so you
can see FormFit AI work without a webcam or a video file.

    python examples/synthetic_demo.py                 # writes demo.mp4 + report.json
    python examples/synthetic_demo.py --gif demo.gif  # also writes a small GIF
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from formfit.config import Settings  # noqa: E402
from formfit.core.types import LANDMARK_NAMES  # noqa: E402
from formfit.feedback import VoiceCoach  # noqa: E402
from formfit.pipeline import WorkoutPipeline  # noqa: E402
from formfit.pose.base import PoseEstimator  # noqa: E402

W, H, FPS = 960, 720, 20
FLOOR = 640
SHIN, THIGH, TORSO = 130.0, 140.0, 160.0


def squat_figure(knee_deg: float, lean_deg: float):
    """Full side-view figure whose hip-knee-ankle angle is ``knee_deg``."""
    ankle = (430.0, float(FLOOR))
    s = math.radians((180 - knee_deg) * 0.3)                    # shin tilts as knees travel forward
    knee = (ankle[0] + SHIN * math.sin(s), ankle[1] - SHIN * math.cos(s))
    to_ankle = (ankle[0] - knee[0], ankle[1] - knee[1])
    norm = math.hypot(*to_ankle)
    ux, uy = to_ankle[0] / norm, to_ankle[1] / norm
    phi = math.radians(knee_deg)
    dx, dy = ux * math.cos(phi) - uy * math.sin(phi), ux * math.sin(phi) + uy * math.cos(phi)
    hip = (knee[0] + THIGH * dx, knee[1] + THIGH * dy)
    lean = math.radians(lean_deg)
    shoulder = (hip[0] + TORSO * math.sin(lean), hip[1] - TORSO * math.cos(lean))
    nose = (shoulder[0] + 28 * math.sin(lean) + 10, shoulder[1] - 45 * math.cos(lean))
    elbow = (shoulder[0] + 45, shoulder[1] + 28)
    wrist = (elbow[0] + 55, elbow[1] - 4)
    pts = {"nose": nose, "shoulder": shoulder, "elbow": elbow, "wrist": wrist,
           "hip": hip, "knee": knee, "ankle": ankle}
    lm = {"nose": (*nose, 1.0)}
    for name in LANDMARK_NAMES[1:]:
        lm[name] = (*pts[name.split("_", 1)[1]], 1.0)
    return lm


def ramp(top: float, bottom: float, frames: int):
    down = [top + (bottom - top) * (0.5 - 0.5 * math.cos(math.pi * i / frames)) for i in range(frames + 1)]
    return down + down[-2::-1]


def script():
    """(knee angle, torso lean) per frame: two clean reps, one shallow, one with a rounded back."""
    frames = []
    frames += [(175.0, 8.0)] * 10
    for bottom, bad_lean in ((88, False), (86, False), (128, False), (90, True)):
        for k in ramp(175, bottom, 22):
            lean = 8 + (175 - k) * 0.22
            if bad_lean and k < 135:
                lean += 30
            frames.append((k, lean))
        frames += [(175.0, 8.0)] * 8
    return frames


class Scripted(PoseEstimator):
    def __init__(self, poses):
        self.poses, self.i = poses, 0

    def process(self, frame_bgr):
        pose = self.poses[min(self.i, len(self.poses) - 1)]
        self.i += 1
        return pose


def background():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        img[y, :] = (46 + y // 18, 40 + y // 20, 38 + y // 22)
    cv2.line(img, (60, FLOOR), (W - 60, FLOOR), (110, 110, 110), 3)
    cv2.putText(img, "SIMULATED SKELETON - synthetic demo", (W - 420, H - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (170, 170, 170), 1, cv2.LINE_AA)
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--out", default="demo.mp4")
    ap.add_argument("--report", default="report.json")
    ap.add_argument("--gif", help="also write a GIF (needs Pillow)")
    args = ap.parse_args()

    frames_spec = script()
    pipe = WorkoutPipeline(Settings(exercise="squat", smoothing=1.0, voice=False),
                           estimator=Scripted([squat_figure(k, l) for k, l in frames_spec]),
                           voice=VoiceCoach(enabled=False))
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    gif_frames = []
    base = background()
    for i in range(len(frames_spec)):
        frame, _ = pipe.process(base.copy(), t=i / FPS)
        writer.write(frame)
        if args.gif and i % 2 == 0:
            gif_frames.append(cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB))
    writer.release()
    summary = pipe.finish()
    pipe.close()

    summary.save_json(args.report)
    print(summary.text())
    print(f"Wrote {args.out} and {args.report}")
    if args.gif:
        from PIL import Image

        imgs = [Image.fromarray(f).convert("P", palette=Image.ADAPTIVE, colors=96) for f in gif_frames]
        imgs[0].save(args.gif, save_all=True, append_images=imgs[1:], duration=100, loop=0, optimize=True)
        print(f"Wrote {args.gif} ({Path(args.gif).stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
