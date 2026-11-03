"""Tests for leakage-safe Phase 2 preparation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_DIR / "src" / "data" / "preparation.py"
SPEC = importlib.util.spec_from_file_location("preparation", MODULE_PATH)
assert SPEC and SPEC.loader
preparation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preparation)


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.features = preparation.build_order_features()
        cls.delivery = preparation.build_delivery_dataset(cls.features)
        cls.dissatisfaction = preparation.build_dissatisfaction_dataset(cls.features)

    def test_features_are_one_row_per_order(self) -> None:
        self.assertEqual(len(self.features), 99441)
        self.assertEqual(self.features["order_id"].nunique(), len(self.features))

    def test_outcome_timestamps_are_not_features(self) -> None:
        forbidden = {
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "review_score",
            "review_creation_date",
            "review_answer_timestamp",
        }
        self.assertTrue(forbidden.isdisjoint(self.features.columns))

    def test_targets_have_expected_eligible_counts(self) -> None:
        self.assertEqual(len(self.delivery), 96476)
        self.assertEqual(int(self.delivery["is_delayed"].sum()), 7827)
        self.assertEqual(len(self.dissatisfaction), 98673)
        self.assertEqual(int(self.dissatisfaction["is_dissatisfied"].sum()), 14475)


if __name__ == "__main__":
    unittest.main()
