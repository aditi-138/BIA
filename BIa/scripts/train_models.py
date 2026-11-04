"""Train both production demo models from processed datasets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.models.train import train_all  # noqa: E402


if __name__ == "__main__":
    print(json.dumps(train_all(), indent=2))
