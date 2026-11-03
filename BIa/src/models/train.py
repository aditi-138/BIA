"""Train leakage-aware baseline models and save real evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config.config import MODELS_DIR, PROCESSED_DATA_DIR, RANDOM_SEED

TARGETS = {"delivery_delay": "is_delayed", "dissatisfaction": "is_dissatisfied"}
ID_COLUMNS = ["order_id", "customer_id"]
DATE_COLUMNS = ["order_purchase_timestamp", "order_approved_at"]


def _split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values("order_purchase_timestamp").reset_index(drop=True)
    n = len(ordered)
    train_end = int(n * 0.70)
    validation_end = int(n * 0.85)
    return ordered.iloc[:train_end], ordered.iloc[train_end:validation_end], ordered.iloc[validation_end:]


def _make_pipeline(
    frame: pd.DataFrame,
    target: str,
    classifier: Any | None = None,
) -> tuple[Pipeline, list[str]]:
    excluded = set(ID_COLUMNS + DATE_COLUMNS + [target])
    features = [column for column in frame.columns if column not in excluded]
    categorical = [column for column in features if frame[column].dtype == "object"]
    numeric = [column for column in features if column not in categorical]
    transformer = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    if classifier is None:
        classifier = LogisticRegression(
            max_iter=500,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        )
    pipeline = Pipeline(
        [
            ("preprocessor", transformer),
            (
                "classifier",
                classifier,
            ),
        ]
    )
    return pipeline, features


def _evaluate(model: Pipeline, data: pd.DataFrame, target: str, features: list[str]) -> dict[str, Any]:
    x = data[features]
    y = data[target].astype(int)
    probabilities = model.predict_proba(x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    matrix = confusion_matrix(y, predictions).tolist()
    return {
        "rows": int(len(data)),
        "positive_rate": float(y.mean()),
        "accuracy": float(accuracy_score(y, predictions)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "confusion_matrix": matrix,
        "threshold": 0.5,
    }


def train_one(name: str, path: Path = PROCESSED_DATA_DIR) -> dict[str, Any]:
    target = TARGETS[name]
    frame = pd.read_csv(path / f"{name}.csv")
    frame["order_purchase_timestamp"] = pd.to_datetime(frame["order_purchase_timestamp"])
    frame["order_approved_at"] = pd.to_datetime(frame["order_approved_at"])
    train, validation, test = _split(frame)
    candidates = {
        "logistic_regression": _make_pipeline(frame, target),
        "random_forest": _make_pipeline(
            frame,
            target,
            RandomForestClassifier(
                n_estimators=180,
                max_depth=14,
                min_samples_leaf=6,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=RANDOM_SEED,
            ),
        ),
    }
    candidate_results: dict[str, dict[str, Any]] = {}
    fitted: dict[str, tuple[Pipeline, list[str]]] = {}
    for candidate_name, (candidate_model, candidate_features) in candidates.items():
        candidate_model.fit(train[candidate_features], train[target].astype(int))
        fitted[candidate_name] = (candidate_model, candidate_features)
        candidate_results[candidate_name] = {
            "train": _evaluate(candidate_model, train, target, candidate_features),
            "validation": _evaluate(candidate_model, validation, target, candidate_features),
            "test": _evaluate(candidate_model, test, target, candidate_features),
        }
    selected_name = max(
        candidate_results,
        key=lambda candidate: candidate_results[candidate]["validation"]["roc_auc"],
    )
    model, features = fitted[selected_name]
    metrics = candidate_results[selected_name]
    artifact = {
        "name": name,
        "target": target,
        "features": features,
        "model": model,
        "metrics": metrics,
        "model_selection": {
            "selected": selected_name,
            "selection_metric": "validation.roc_auc",
            "candidates": candidate_results,
        },
        "split": {"train": 0.70, "validation": 0.15, "test": 0.15},
    }
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODELS_DIR / f"{name}.joblib")
    return {
        "name": name,
        "target": target,
        "metrics": metrics,
        "model_selection": artifact["model_selection"],
    }


def train_all() -> dict[str, Any]:
    results = {name: train_one(name) for name in TARGETS}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    (MODELS_DIR / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    print(json.dumps(train_all(), indent=2))
