from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.risk import classify_risk


class RiskTests(unittest.TestCase):
    def test_risk_matrix(self) -> None:
        self.assertEqual(classify_risk(0.8, 0.8), "Highest intervention priority")
        self.assertEqual(classify_risk(0.8, 0.2), "Delivery monitoring")
        self.assertEqual(classify_risk(0.2, 0.8), "Investigate non-delivery causes")
        self.assertEqual(classify_risk(0.2, 0.2), "Normal monitoring")


if __name__ == "__main__":
    unittest.main()
