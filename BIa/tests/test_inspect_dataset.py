"""Focused tests for the Phase 1 inspection utility."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_DIR / "scripts" / "inspect_dataset.py"
SPEC = importlib.util.spec_from_file_location("inspect_dataset", SCRIPT_PATH)
assert SPEC and SPEC.loader
inspect_dataset = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspect_dataset)


class InspectDatasetTests(unittest.TestCase):
    def test_complete_dataset_is_reported_as_ready(self) -> None:
        report = inspect_dataset.build_report()

        self.assertEqual(report["available_file_count"], 9)
        self.assertEqual(report["missing_file_count"], 0)
        self.assertTrue(report["target_readiness"]["complete_raw_dataset"])
        self.assertTrue(report["target_readiness"]["delivery_delay_target_ready"])
        self.assertTrue(report["target_readiness"]["dissatisfaction_target_ready"])
        self.assertEqual(
            report["relationship_checks"]["orders_to_customers"]["unmatched_rows"], 0
        )

    def test_customer_inventory_contains_actual_dimensions_and_schema(self) -> None:
        customers = inspect_dataset.build_report()["files"]["customers"]

        self.assertEqual(customers["status"], "inspected")
        self.assertEqual(customers["rows"], 99441)
        self.assertEqual(customers["columns"], 5)
        self.assertEqual(customers["missing_required_columns"], [])
        self.assertIn("customer_id", customers["column_names"])

    def test_report_is_json_serializable(self) -> None:
        report = inspect_dataset.build_report()
        json.dumps(report)

    def test_markdown_rendering_exposes_missing_inputs(self) -> None:
        report = inspect_dataset.build_report()
        markdown = inspect_dataset.render_markdown(report)

        self.assertIn("# Dataset Inventory", markdown)
        self.assertIn("| `orders` | Inspected | 99441 | 8 |", markdown)
        self.assertIn("| `customers` | Inspected | 99441 | 5 |", markdown)


if __name__ == "__main__":
    unittest.main()
