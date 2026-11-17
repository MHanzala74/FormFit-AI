"""FormFit AI - AI Gym Trainer & Posture Corrector (entry point).

Examples:
    python main.py --exercise squat
    python main.py --exercise pushup --backend yolo
    python main.py --exercise squat --video workout.mp4 --no-voice
"""

from __future__ import annotations

import argparse
import sys

import cv2

from trainer.exercises import EXERCISES, create_exercise
from trainer.feedback import VoiceCoach
from trainer.pose_estimator import create_estimator, draw_skeleton

GREEN, RED, WHITE = (60, 220, 60), (60, 60, 240), (255, 255, 255)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Gym Trainer & Posture Corrector")
    p.add_argument("--exercise", choices=sorted(EXERCISES), default="squat")
    p.add_argument("--backend", choices=["mediapipe", "yolo"], default="mediapipe")
    p.add_argument("--camera", type=int, default=0, help="webcam index")
    p.add_argument("--video", help="path to a video file instead of the webcam")
    p.add_argument("--no-voice", action="store_true", help="disable voice feedback")
    return p.parse_args()


def draw_hud(frame, analysis, exercise_name: str) -> None:
    color = GREEN if analysis.posture_ok else RED
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 90), (30, 30, 30), -1)
    cv2.putText(frame, f"{exercise_name.upper()}  Reps: {analysis.reps}  Stage: {analysis.stage}",
                (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, WHITE, 2)
    y = 70
    angles = "  ".join(f"{k}: {v:.0f}" for k, v in analysis.angles.items())
    cv2.putText(frame, angles, (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    for i, msg in enumerate(analysis.warnings):
        cv2.putText(frame, msg, (15, 130 + 35 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.9, RED, 2)
    if analysis.posture_ok and analysis.angles:
        cv2.putText(frame, "Good form", (15, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, GREEN, 2)


def main() -> int:
    args = parse_args()
    cap = cv2.VideoCapture(args.video if args.video else args.camera)
    if not cap.isOpened():
        print("Could not open the video source.", file=sys.stderr)
        return 1

    estimator = create_estimator(args.backend)
    exercise = create_exercise(args.exercise)
    coach = VoiceCoach(enabled=not args.no_voice)
    coach.say(f"Starting {exercise.name}. Get into position.", force=True)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if not args.video:
                frame = cv2.flip(frame, 1)  # mirror view for webcam

            landmarks = estimator.process(frame)
            analysis = exercise.analyze(landmarks)

            if landmarks:
                draw_skeleton(frame, landmarks)
            if analysis.rep_completed:
                coach.rep(analysis.reps)
            for msg in analysis.warnings:
                coach.say(msg)
            draw_hud(frame, analysis, exercise.name)

            cv2.imshow("FormFit AI", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        coach.say(f"Workout finished. {exercise.reps} reps.", force=True)
        cap.release()
        cv2.destroyAllWindows()
        estimator.close()
        coach.close()
    print(f"Total reps: {exercise.reps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
