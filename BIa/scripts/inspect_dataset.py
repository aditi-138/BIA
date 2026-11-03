"""Inspect the locally available Olist CSV files for Phase 1.

The script deliberately reports missing files instead of inventing a complete
dataset inventory. It can be run before the full dataset is available to
diagnose setup, and rerun after all expected CSVs have been copied to
``BIa/data/raw``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from config.config import OLIST_RAW_FILES, RAW_DATA_DIR, ensure_directories  # noqa: E402

KEY_COLUMNS: dict[str, tuple[str, ...]] = {
    "orders": ("order_id",),
    "order_items": ("order_id", "order_item_id"),
    "order_payments": ("order_id", "payment_sequential"),
    "order_reviews": ("review_id", "order_id"),
    "customers": ("customer_id",),
    "products": ("product_id",),
    "sellers": ("seller_id",),
    "geolocation": ("geolocation_zip_code_prefix",),
    "category_translation": ("product_category_name",),
}

TIMESTAMP_COLUMNS: dict[str, tuple[str, ...]] = {
    "orders": (
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
    "order_reviews": ("review_creation_date", "review_answer_timestamp"),
}

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "orders": (
        "order_id",
        "customer_id",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
    "order_items": ("order_id", "order_item_id", "product_id", "seller_id"),
    "order_payments": ("order_id", "payment_sequential", "payment_value"),
    "order_reviews": ("review_id", "order_id", "review_score"),
    "customers": ("customer_id", "customer_unique_id"),
    "products": ("product_id", "product_category_name"),
    "sellers": ("seller_id", "seller_zip_code_prefix"),
    "geolocation": ("geolocation_zip_code_prefix", "geolocation_lat"),
    "category_translation": ("product_category_name", "product_category_name_english"),
}

RELATIONSHIPS: tuple[dict[str, str], ...] = (
    {"from": "orders.customer_id", "to": "customers.customer_id", "cardinality": "many-to-one"},
    {"from": "order_items.order_id", "to": "orders.order_id", "cardinality": "many-to-one"},
    {"from": "order_items.product_id", "to": "products.product_id", "cardinality": "many-to-one"},
    {"from": "order_items.seller_id", "to": "sellers.seller_id", "cardinality": "many-to-one"},
    {"from": "order_payments.order_id", "to": "orders.order_id", "cardinality": "many-to-one"},
    {"from": "order_reviews.order_id", "to": "orders.order_id", "cardinality": "many-to-one"},
    {
        "from": "products.product_category_name",
        "to": "category_translation.product_category_name",
        "cardinality": "many-to-one",
    },
)


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def inspect_file(name: str, filename: str) -> dict[str, Any]:
    """Return dimensions, schema, missingness, keys, and date ranges."""
    path = RAW_DATA_DIR / filename
    if not path.exists():
        return {
            "status": "missing",
            "path": str(path),
            "filename": filename,
        }

    frame = pd.read_csv(path)
    missing = frame.isna().sum()
    duplicate_rows = int(frame.duplicated().sum())
    key_report: dict[str, Any] = {}
    for column in KEY_COLUMNS.get(name, ()):
        if column not in frame.columns:
            key_report[column] = {"present": False}
            continue
        key_report[column] = {
            "present": True,
            "missing": int(frame[column].isna().sum()),
            "unique": int(frame[column].nunique(dropna=True)),
            "duplicate_values": int(frame[column].duplicated(keep=False).sum()),
        }

    date_ranges: dict[str, Any] = {}
    for column in TIMESTAMP_COLUMNS.get(name, ()):
        if column not in frame.columns:
            date_ranges[column] = {"present": False}
            continue
        dates = pd.to_datetime(frame[column], errors="coerce")
        date_ranges[column] = {
            "present": True,
            "invalid_or_missing": int(dates.isna().sum()),
            "minimum": _json_safe(dates.min()),
            "maximum": _json_safe(dates.max()),
        }

    missing_required_columns = [
        column for column in REQUIRED_COLUMNS.get(name, ()) if column not in frame.columns
    ]
    return {
        "status": "inspected",
        "path": str(path),
        "filename": filename,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "column_names": list(frame.columns),
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "missing_values": {
            column: int(count) for column, count in missing.items() if count
        },
        "duplicate_rows": duplicate_rows,
        "missing_required_columns": missing_required_columns,
        "keys": key_report,
        "timestamp_ranges": date_ranges,
    }


def build_report() -> dict[str, Any]:
    """Inspect every expected file without requiring all files to exist."""
    ensure_directories()
    files = {
        name: inspect_file(name, filename)
        for name, filename in OLIST_RAW_FILES.items()
    }
    missing = [
        result["filename"]
        for result in files.values()
        if result["status"] == "missing"
    ]
    schema_issues = {
        name: result["missing_required_columns"]
        for name, result in files.items()
        if result["status"] == "inspected" and result["missing_required_columns"]
    }
    readiness = {
        "complete_raw_dataset": not missing,
        "required_columns_present": not schema_issues,
        "delivery_delay_target_ready": not missing
        and not schema_issues
        and "orders" in files,
        "dissatisfaction_target_ready": not missing
        and not schema_issues
        and "orders" in files
        and "order_reviews" in files,
    }
    relationship_checks: dict[str, Any] = {}
    target_analysis: dict[str, Any] = {}
    if not missing and not schema_issues:
        relationship_checks, target_analysis = analyze_dataset()
    return {
        "project": "Olist delivery delay and dissatisfaction analytics",
        "raw_data_directory": str(RAW_DATA_DIR),
        "expected_file_count": len(OLIST_RAW_FILES),
        "available_file_count": len(OLIST_RAW_FILES) - len(missing),
        "missing_file_count": len(missing),
        "missing_files": missing,
        "schema_issues": schema_issues,
        "relationships": list(RELATIONSHIPS),
        "target_readiness": readiness,
        "relationship_checks": relationship_checks,
        "target_analysis": target_analysis,
        "files": files,
    }


def analyze_dataset() -> tuple[dict[str, Any], dict[str, Any]]:
    """Calculate target feasibility and foreign-key evidence on full inputs."""
    orders = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["orders"])
    customers = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["customers"])
    items = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["order_items"])
    payments = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["order_payments"])
    reviews = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["order_reviews"])
    products = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["products"])
    sellers = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["sellers"])
    translation = pd.read_csv(RAW_DATA_DIR / OLIST_RAW_FILES["category_translation"])

    def coverage(left: pd.Series, right: pd.Series) -> dict[str, Any]:
        values = left.dropna().astype(str)
        reference = set(right.dropna().astype(str))
        unmatched = int((~values.isin(reference)).sum())
        return {
            "rows_checked": int(len(values)),
            "unmatched_rows": unmatched,
            "coverage_rate": float((len(values) - unmatched) / len(values))
            if len(values)
            else None,
        }

    relationship_checks = {
        "orders_to_customers": coverage(orders["customer_id"], customers["customer_id"]),
        "items_to_orders": coverage(items["order_id"], orders["order_id"]),
        "items_to_products": coverage(items["product_id"], products["product_id"]),
        "items_to_sellers": coverage(items["seller_id"], sellers["seller_id"]),
        "payments_to_orders": coverage(payments["order_id"], orders["order_id"]),
        "reviews_to_orders": coverage(reviews["order_id"], orders["order_id"]),
        "products_to_translation": coverage(
            products["product_category_name"], translation["product_category_name"]
        ),
    }

    delivered = pd.to_datetime(orders["order_delivered_customer_date"], errors="coerce")
    estimated = pd.to_datetime(orders["order_estimated_delivery_date"], errors="coerce")
    delay_eligible = delivered.notna() & estimated.notna()
    delayed = (delivered > estimated) & delay_eligible
    score = pd.to_numeric(reviews["review_score"], errors="coerce")
    dissatisfaction_eligible = score.notna()
    dissatisfied = score.isin((1, 2)) & dissatisfaction_eligible
    target_analysis = {
        "delivery_delay": {
            "eligible_rows": int(delay_eligible.sum()),
            "excluded_rows": int((~delay_eligible).sum()),
            "positive_rows": int(delayed.sum()),
            "positive_rate": float(delayed[delay_eligible].mean())
            if delay_eligible.any()
            else None,
            "definition": "order_delivered_customer_date > order_estimated_delivery_date",
        },
        "customer_dissatisfaction": {
            "review_rows": int(len(reviews)),
            "unique_review_orders": int(reviews["order_id"].nunique()),
            "eligible_rows": int(dissatisfaction_eligible.sum()),
            "excluded_rows": int((~dissatisfaction_eligible).sum()),
            "positive_rows": int(dissatisfied.sum()),
            "positive_rate": float(dissatisfied[dissatisfaction_eligible].mean())
            if dissatisfaction_eligible.any()
            else None,
            "definition": "review_score in {1, 2}",
        },
    }
    return relationship_checks, target_analysis


def write_report(report: dict[str, Any], output: Path | None) -> None:
    payload = json.dumps(report, indent=2, default=_json_safe)
    if output is None:
        print(payload)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")
    print(f"Wrote inspection report: {output}")


def render_markdown(report: dict[str, Any]) -> str:
    """Render a concise, evidence-based inventory from a JSON report."""
    lines = [
        "# Dataset Inventory",
        "",
        "Generated from the locally available files; missing inputs are not inferred.",
        "",
        "## Readiness",
        "",
        f"- Expected files: {report['expected_file_count']}",
        f"- Available files: {report['available_file_count']}",
        f"- Missing files: {report['missing_file_count']}",
    ]
    for name, ready in report["target_readiness"].items():
        lines.append(f"- `{name}`: {'ready' if ready else 'not ready'}")

    lines.extend(["", "## File inventory", "", "| Table | Status | Rows | Columns | Duplicate rows |", "|---|---|---:|---:|---:|"])
    for name, result in report["files"].items():
        if result["status"] == "missing":
            lines.append(f"| `{name}` | Missing | — | — | — |")
        else:
            lines.append(
                f"| `{name}` | Inspected | {result['rows']} | {result['columns']} | "
                f"{result['duplicate_rows']} |"
            )

    if report["missing_files"]:
        lines.extend(["", "## Missing files", ""])
        lines.extend(f"- `{filename}`" for filename in report["missing_files"])
    if report["schema_issues"]:
        lines.extend(["", "## Schema issues", ""])
        for name, columns in report["schema_issues"].items():
            lines.append(f"- `{name}` is missing: {', '.join(f'`{column}`' for column in columns)}")

    lines.extend(["", "## Declared relationships", "", "| From | To | Cardinality |", "|---|---|---|"])
    lines.extend(
        f"| `{relationship['from']}` | `{relationship['to']}` | {relationship['cardinality']} |"
        for relationship in report["relationships"]
    )
    lines.append("")
    if report["relationship_checks"]:
        lines.extend(["## Relationship checks", "", "| Relationship | Unmatched rows | Coverage |", "|---|---:|---:|"])
        for name, result in report["relationship_checks"].items():
            lines.append(
                f"| `{name}` | {result['unmatched_rows']} | "
                f"{result['coverage_rate']:.4%} |"
            )
    if report["target_analysis"]:
        lines.extend(["", "## Target feasibility", "", "| Target | Eligible rows | Excluded rows | Positive rows | Positive rate |", "|---|---:|---:|---:|---:|"])
        for name, result in report["target_analysis"].items():
            lines.append(
                f"| `{name}` | {result['eligible_rows']} | {result['excluded_rows']} | "
                f"{result['positive_rows']} | {result['positive_rate']:.4%} |"
            )
    lines.append("")
    return "\n".join(lines)


def write_markdown(report: dict[str, Any], output: Path | None) -> None:
    """Write the human-readable inventory when an output path is supplied."""
    if output is None:
        print(render_markdown(report))
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote Markdown inventory: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path, relative to the current directory.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="Optional Markdown inventory path, relative to the current directory.",
    )
    args = parser.parse_args()
    report = build_report()
    write_report(report, args.output)
    write_markdown(report, args.markdown_output)
    if report["missing_file_count"]:
        print(
            f"Dataset incomplete: {report['missing_file_count']} expected file(s) "
            "are missing.",
            file=sys.stderr,
        )
        return 2
    print("Dataset inspection completed for all expected files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
