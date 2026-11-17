# Contributing to FormFit AI

Thanks for helping out! The easiest first contribution is a new exercise.

## Setup

```bash
git clone https://github.com/MHanzala74/FormFit-AI.git
cd FormFit-AI
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
```

## Workflow

1. Create a branch: `git checkout -b feature/deadlift`
2. Make your change, with tests (`tests/helpers.py` builds synthetic poses - no camera needed)
3. `make test && make lint`
4. Open a pull request using the template

## Adding an exercise

See [docs/architecture.md](docs/architecture.md#adding-an-exercise). Keep the geometry in `measure()` and the posture rules in
`check_form()`; the base class handles counting, tempo and scoring.

## Style

- Python 3.10+, type hints on public functions, `ruff` clean
- Keep `formfit.core`, `formfit.exercises` and `formfit.session` free of heavy dependencies so tests stay fast
- Commit messages: short imperative summary ("Add deadlift analyzer"), details in the body
