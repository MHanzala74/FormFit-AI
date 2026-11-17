"""Convenience launcher so ``python main.py run -e squat`` works without installing the package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from formfit.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
