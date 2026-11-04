"""Build leakage-safe, order-level modelling datasets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.data.preparation import prepare_datasets  # noqa: E402


def main() -> int:
    datasets = prepare_datasets()
    summary = {
        name: {
            "rows": int(len(frame)),
            "columns": int(len(frame.columns)),
            "positive_rate": (
                float(frame[target].mean())
                if (target := next(
                    (column for column in ("is_delayed", "is_dissatisfied")
                     if column in frame.columns),
                    None,
                ))
                else None
            ),
        }
        for name, frame in datasets.items()
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
