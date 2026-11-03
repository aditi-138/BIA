"""Integrated order-level risk policy."""

from __future__ import annotations

import pandas as pd


def classify_risk(
    delay_probability: float,
    dissatisfaction_probability: float,
    threshold: float = 0.5,
) -> str:
    high_delay = delay_probability >= threshold
    high_dissatisfaction = dissatisfaction_probability >= threshold
    if high_delay and high_dissatisfaction:
        return "Highest intervention priority"
    if high_delay:
        return "Delivery monitoring"
    if high_dissatisfaction:
        return "Investigate non-delivery causes"
    return "Normal monitoring"


def add_risk_categories(
    frame: pd.DataFrame,
    delay_probability: pd.Series,
    dissatisfaction_probability: pd.Series,
    threshold: float = 0.5,
) -> pd.DataFrame:
    result = frame.copy()
    result["delay_probability"] = delay_probability
    result["dissatisfaction_probability"] = dissatisfaction_probability
    result["risk_category"] = [
        classify_risk(delay, dissatisfaction, threshold)
        for delay, dissatisfaction in zip(delay_probability, dissatisfaction_probability)
    ]
    return result
