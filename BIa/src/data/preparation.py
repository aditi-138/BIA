"""Leakage-aware order-level feature preparation for the Olist dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from config.config import OLIST_RAW_FILES, PROCESSED_DATA_DIR, RAW_DATA_DIR

ORDER_FEATURES: Final[tuple[str, ...]] = (
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "customer_city",
    "customer_state",
    "item_count",
    "unique_product_count",
    "unique_seller_count",
    "total_price",
    "total_freight_value",
    "payment_count",
    "payment_value_total",
    "credit_card_payment_count",
    "seller_state_count",
    "product_category_count",
)


def _read(name: str, data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(data_dir / OLIST_RAW_FILES[name])


def build_order_features(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Build one row per order using features available before outcomes."""
    orders = _read("orders", data_dir)
    customers = _read("customers", data_dir)
    items = _read("order_items", data_dir)
    payments = _read("order_payments", data_dir)
    products = _read("products", data_dir)
    sellers = _read("sellers", data_dir)

    orders = orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
        ]
    ].copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders["order_approved_at"] = pd.to_datetime(
        orders["order_approved_at"], errors="coerce"
    )

    customer_features = customers[
        ["customer_id", "customer_city", "customer_state"]
    ].drop_duplicates("customer_id")
    items_enriched = items.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    ).merge(
        sellers[["seller_id", "seller_state"]],
        on="seller_id",
        how="left",
        validate="many_to_one",
    )
    item_features = items_enriched.groupby("order_id", as_index=False).agg(
        item_count=("order_item_id", "count"),
        unique_product_count=("product_id", "nunique"),
        unique_seller_count=("seller_id", "nunique"),
        total_price=("price", "sum"),
        total_freight_value=("freight_value", "sum"),
        seller_state_count=("seller_state", "nunique"),
        product_category_count=("product_category_name", "nunique"),
    )
    payment_features = payments.assign(
        is_credit_card=payments["payment_type"].eq("credit_card").astype("int8")
    ).groupby("order_id", as_index=False).agg(
        payment_count=("payment_sequential", "count"),
        payment_value_total=("payment_value", "sum"),
        credit_card_payment_count=("is_credit_card", "sum"),
    )
    features = (
        orders.merge(customer_features, on="customer_id", how="left", validate="many_to_one")
        .merge(item_features, on="order_id", how="left", validate="one_to_one")
        .merge(payment_features, on="order_id", how="left", validate="one_to_one")
    )
    numeric = [
        "item_count",
        "unique_product_count",
        "unique_seller_count",
        "total_price",
        "total_freight_value",
        "payment_count",
        "payment_value_total",
        "credit_card_payment_count",
        "seller_state_count",
        "product_category_count",
    ]
    features[numeric] = features[numeric].fillna(0)
    return features[list(ORDER_FEATURES)]


def build_delivery_dataset(
    order_features: pd.DataFrame, data_dir: Path = RAW_DATA_DIR
) -> pd.DataFrame:
    """Attach the delivery target and retain only target-eligible orders."""
    orders = _read("orders", data_dir)[
        ["order_id", "order_delivered_customer_date", "order_estimated_delivery_date"]
    ]
    orders["delivered"] = pd.to_datetime(
        orders["order_delivered_customer_date"], errors="coerce"
    )
    orders["estimated"] = pd.to_datetime(
        orders["order_estimated_delivery_date"], errors="coerce"
    )
    orders = orders.dropna(subset=["delivered", "estimated"])
    orders["is_delayed"] = (orders["delivered"] > orders["estimated"]).astype("int8")
    return order_features.merge(
        orders[["order_id", "is_delayed"]],
        on="order_id",
        how="inner",
        validate="one_to_one",
    )


def build_dissatisfaction_dataset(
    order_features: pd.DataFrame, data_dir: Path = RAW_DATA_DIR
) -> pd.DataFrame:
    """Attach the first review per order as the dissatisfaction target."""
    reviews = _read("order_reviews", data_dir)
    reviews["review_creation_date"] = pd.to_datetime(
        reviews["review_creation_date"], errors="coerce"
    )
    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
    reviews = (
        reviews.dropna(subset=["order_id", "review_score"])
        .sort_values(["order_id", "review_creation_date", "review_id"])
        .drop_duplicates("order_id", keep="first")
    )
    reviews["is_dissatisfied"] = reviews["review_score"].isin((1, 2)).astype("int8")
    return order_features.merge(
        reviews[["order_id", "is_dissatisfied"]],
        on="order_id",
        how="inner",
        validate="one_to_one",
    )


def prepare_datasets(
    data_dir: Path = RAW_DATA_DIR, output_dir: Path = PROCESSED_DATA_DIR
) -> dict[str, pd.DataFrame]:
    """Build and optionally save both order-level modelling datasets."""
    features = build_order_features(data_dir)
    datasets = {
        "order_features": features,
        "delivery_delay": build_delivery_dataset(features, data_dir),
        "dissatisfaction": build_dissatisfaction_dataset(features, data_dir),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in datasets.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    return datasets
