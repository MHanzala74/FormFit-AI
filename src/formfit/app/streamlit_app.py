"""Streamlit web app: upload a workout video and get rep counts, form scores and tips.

Run with:  streamlit run src/formfit/app/streamlit_app.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# Allow running straight from a checkout without `pip install -e .`
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from formfit.config import Settings  # noqa: E402
from formfit.exercises import EXERCISES, create_exercise  # noqa: E402
from formfit.pipeline import run_video  # noqa: E402
from formfit.pose import BACKENDS  # noqa: E402

st.set_page_config(page_title="FormFit AI", page_icon="🏋️", layout="wide")

st.title("🏋️ FormFit AI")
st.caption("AI gym trainer & posture corrector - upload a side-view workout clip and get "
           "rep counts, form scores and coaching feedback.")

with st.sidebar:
    st.header("Settings")
    exercise = st.selectbox("Exercise", sorted(EXERCISES),
                            format_func=lambda n: create_exercise(n).display_name)
    st.caption(create_exercise(exercise).description)
    backend = st.selectbox("Pose backend", BACKENDS,
                           help="'yolo' requires: pip install 'formfit-ai[yolo]'")
    smoothing = st.slider("Smoothing", 0.1, 1.0, 0.6, 0.05,
                          help="Lower = steadier skeleton but more lag. 1.0 disables it.")
    make_video = st.checkbox("Create annotated video", value=True)

upload = st.file_uploader("Workout video", type=["mp4", "mov", "avi", "mkv"])
st.info("Film from the **side** with your whole body in frame for the most reliable angles.")

if upload and st.button("Analyze", type="primary"):
    workdir = Path(tempfile.mkdtemp(prefix="formfit_"))
    src = workdir / upload.name
    src.write_bytes(upload.getbuffer())
    out = workdir / "annotated.mp4" if make_video else None

    bar = st.progress(0.0, text="Analyzing...")

    def on_progress(done: int, total: int) -> None:
        if total:
            bar.progress(min(done / total, 1.0), text=f"Analyzing frame {done}/{total}")

    try:
        summary = run_video(str(src), Settings(exercise=exercise, backend=backend,
                                               smoothing=smoothing),
                            output=str(out) if out else None, progress=on_progress)
    except Exception as exc:  # surface backend/IO problems in the UI
        st.error(f"Analysis failed: {exc}")
        st.stop()
    bar.empty()

    unit = "Holds" if exercise == "plank" else "Reps"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(unit, summary.total_reps)
    c2.metric("Avg form score", f"{summary.avg_form_score:.0f}/100")
    c3.metric("Duration", f"{summary.duration_seconds:.1f}s")
    c4.metric("Frames", summary.frames)

    if summary.reps:
        df = pd.DataFrame([{
            "rep": r.number, "time (s)": round(r.timestamp, 1), "duration (s)": round(r.duration, 2),
            "peak angle": round(r.peak_angle, 1), "score": round(r.score),
            "issues": ", ".join(r.issues) or "-",
        } for r in summary.reps])
        left, right = st.columns([3, 2])
        left.subheader("Per-rep results")
        left.dataframe(df, use_container_width=True, hide_index=True)
        right.subheader("Form score by rep")
        right.bar_chart(df.set_index("rep")["score"])
        if summary.common_issues:
            st.subheader("What to work on")
            for issue, count in summary.common_issues:
                st.write(f"- **{issue}** ({count}x)")
    else:
        st.warning("No completed reps were detected. Check the camera angle, lighting and "
                   "that your full body is visible.")

    st.subheader("Downloads")
    d1, d2, d3 = st.columns(3)
    summary.save_json(workdir / "report.json")
    summary.save_csv(workdir / "report.csv")
    d1.download_button("Report (JSON)", (workdir / "report.json").read_bytes(),
                       "formfit_report.json", "application/json")
    d2.download_button("Reps (CSV)", (workdir / "report.csv").read_bytes(),
                       "formfit_reps.csv", "text/csv")
    if out and out.exists():
        d3.download_button("Annotated video", out.read_bytes(), "formfit_annotated.mp4", "video/mp4")
