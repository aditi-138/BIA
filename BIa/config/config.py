"""
Central project configuration.

All notebooks and modules should import from this file (or from src)
so that paths, seeds and modelling defaults stay consistent.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED: int = 42

# ---------------------------------------------------------------------------
# Project paths (resolved relative to the repository root)
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
INTERIM_DATA_DIR: Path = DATA_DIR / "interim"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
EXTERNAL_DATA_DIR: Path = DATA_DIR / "external"

MODELS_DIR: Path = PROJECT_ROOT / "models"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
FIGURES_DIR: Path = REPORTS_DIR / "figures"
NOTEBOOKS_DIR: Path = PROJECT_ROOT / "notebooks"
DOCS_DIR: Path = PROJECT_ROOT / "docs"

# Expected Olist raw CSV filenames (official Brazilian E-Commerce dataset)
OLIST_RAW_FILES: dict[str, str] = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# ---------------------------------------------------------------------------
# Prediction points (confirmed in Phase 0; refined after data inspection)
# ---------------------------------------------------------------------------
# Delivery delay: predict after order approval, before actual delivery occurs.
# Features must be known at or before this point (no actual delivery timestamps).
DELIVERY_DELAY_PREDICTION_POINT: str = "order_approved_at"

# Dissatisfaction: predict before the customer submits a review.
# Features must exclude review text, review dates, and review scores.
DISSATISFACTION_PREDICTION_POINT: str = "pre_review_submission"

# ---------------------------------------------------------------------------
# Target definitions (construction details in Phase 1–2)
# ---------------------------------------------------------------------------
# Delay: actual delivery timestamp > estimated delivery timestamp
DELAY_TARGET_NAME: str = "is_delayed"

# Dissatisfaction: review_score in {1, 2}
LOW_REVIEW_SCORES: tuple[int, ...] = (1, 2)
DISSATISFACTION_TARGET_NAME: str = "is_dissatisfied"

# ---------------------------------------------------------------------------
# Chronological split defaults (ratios of ordered samples; Phase 4–5 may refine)
# ---------------------------------------------------------------------------
TEMPORAL_SPLIT_RATIOS: dict[str, float] = {
    "train": 0.70,
    "validation": 0.15,
    "test": 0.15,
}

# ---------------------------------------------------------------------------
# Risk engine category labels (logic implemented in Phase 6)
# ---------------------------------------------------------------------------
RISK_CATEGORIES: dict[str, str] = {
    "high_delay_high_dissatisfaction": "Highest intervention priority",
    "high_delay_low_dissatisfaction": "Delivery monitoring",
    "low_delay_high_dissatisfaction": "Investigate non-delivery causes",
    "low_delay_low_dissatisfaction": "Normal monitoring",
}


def ensure_directories() -> None:
    """Create standard project directories if they do not already exist."""
    for path in (
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        MODELS_DIR,
        FIGURES_DIR,
        NOTEBOOKS_DIR,
        DOCS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def list_missing_raw_files() -> list[str]:
    """Return names of expected Olist CSVs that are not present in data/raw."""
    missing: list[str] = []
    for filename in OLIST_RAW_FILES.values():
        if not (RAW_DATA_DIR / filename).exists():
            missing.append(filename)
    return missing


if __name__ == "__main__":
    ensure_directories()
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"RANDOM_SEED:  {RANDOM_SEED}")
    print(f"Delivery prediction point: {DELIVERY_DELAY_PREDICTION_POINT}")
    print(f"Dissatisfaction prediction point: {DISSATISFACTION_PREDICTION_POINT}")
    missing = list_missing_raw_files()
    if missing:
        print(f"Missing raw files ({len(missing)}):")
        for name in missing:
            print(f"  - {name}")
    else:
        print("All expected Olist raw CSV files are present in data/raw.")
