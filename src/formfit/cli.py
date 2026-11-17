"""Command line interface: ``formfit run | analyze | list``."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from formfit import __version__
from formfit.config import Settings
from formfit.exercises import EXERCISES
from formfit.pose import BACKENDS


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("-e", "--exercise", choices=sorted(EXERCISES), default="squat")
    p.add_argument("-b", "--backend", choices=BACKENDS, default="mediapipe",
                   help="pose estimation backend (yolo needs: pip install 'formfit-ai[yolo]')")
    p.add_argument("--smoothing", type=float, default=0.6,
                   help="landmark smoothing alpha in (0,1]; 1 disables (default 0.6)")
    p.add_argument("--report", metavar="FILE", help="save the session summary as JSON")
    p.add_argument("--csv", metavar="FILE", help="save per-rep results as CSV")
    p.add_argument("--no-skeleton", action="store_true", help="hide the skeleton overlay")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="formfit", description="FormFit AI - real-time AI gym trainer & posture corrector")
    parser.add_argument("--version", action="version", version=f"formfit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="live coaching from a webcam")
    _common(run)
    run.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
    run.add_argument("--no-voice", action="store_true", help="disable voice feedback")
    run.add_argument("--no-mirror", action="store_true", help="do not mirror the preview")
    run.add_argument("--record", metavar="FILE", help="save the annotated session to an .mp4")

    ana = sub.add_parser("analyze", help="analyse a recorded video offline")
    ana.add_argument("video", help="path to the input video")
    _common(ana)
    ana.add_argument("-o", "--output", metavar="FILE", help="write an annotated .mp4")
    ana.add_argument("--show", action="store_true", help="preview while processing")

    sub.add_parser("list", help="list supported exercises")
    return parser


def _settings(args, voice: bool) -> Settings:
    return Settings(exercise=args.exercise, backend=args.backend, smoothing=args.smoothing,
                    voice=voice, mirror=not getattr(args, "no_mirror", False),
                    show_skeleton=not args.no_skeleton)


def _export(summary, args) -> None:
    print(summary.text())
    if args.report:
        print(f"Saved JSON report -> {summary.save_json(args.report)}")
    if args.csv:
        print(f"Saved CSV         -> {summary.save_csv(args.csv)}")


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "list":
        from formfit.exercises import create_exercise

        for name in sorted(EXERCISES):
            ex = create_exercise(name)
            print(f"{name:<8} {ex.display_name:<11} {ex.description}")
        return 0

    from formfit import pipeline  # heavy imports (OpenCV/MediaPipe) only when needed

    try:
        if args.command == "run":
            summary = pipeline.run_webcam(_settings(args, voice=not args.no_voice),
                                          camera=args.camera, record=args.record)
        else:
            def progress(done: int, total: int) -> None:
                if total and done % 30 == 0:
                    print(f"\rProcessing {done}/{total} frames", end="", file=sys.stderr)

            summary = pipeline.run_video(args.video, _settings(args, voice=False),
                                         output=args.output, show=args.show, progress=progress)
            print(file=sys.stderr)
            if args.output:
                print(f"Saved annotated video -> {args.output}")
    except (RuntimeError, FileNotFoundError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _export(summary, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
