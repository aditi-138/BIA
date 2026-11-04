# Phase 1 Data Dictionary and Leakage Notes

This document records the intended role of each official Olist table and the
columns that require special treatment. It is an analysis guide, not a claim
that all tables have been inspected locally.

## Table roles and safe joins

| Table | Intended grain | Primary/key fields | Intended use |
|---|---|---|---|
| `olist_orders_dataset.csv` | One row per order | `order_id`, `customer_id` | Order lifecycle, prediction grain, and target construction |
| `olist_order_items_dataset.csv` | One row per order item | `order_id`, `order_item_id`, `product_id`, `seller_id` | Aggregate item, seller, price, freight, and shipping features to order grain |
| `olist_order_payments_dataset.csv` | One row per payment event | `order_id`, `payment_sequential` | Aggregate payment count/value and payment-type features to order grain |
| `olist_order_reviews_dataset.csv` | Review record associated with an order | `review_id`, `order_id` | Construct dissatisfaction target; exclude review outcome fields from inputs |
| `olist_customers_dataset.csv` | One row per customer-order key | `customer_id`, `customer_unique_id` | Join customer location to orders; avoid assuming unique customer-order history without checking |
| `olist_products_dataset.csv` | One row per product | `product_id` | Product category and dimensions joined through order items |
| `olist_sellers_dataset.csv` | One row per seller | `seller_id` | Seller location joined through order items |
| `olist_geolocation_dataset.csv` | Multiple rows per ZIP prefix | `geolocation_zip_code_prefix` | Use only after deciding how repeated ZIP-prefix coordinates are aggregated |
| `product_category_name_translation.csv` | One row per Portuguese category | `product_category_name` | Optional category labels; preserve untranslated values |

Joins from item, payment, and review tables can multiply rows. The modelling
dataset should be order-level, so each one-to-many table must be aggregated or
deduplicated according to a documented rule before joining to orders.

## Target and leakage rules

### Delivery delay

Proposed target:

`is_delayed = order_delivered_customer_date > order_estimated_delivery_date`

The prediction point is `order_approved_at`. Actual delivery timestamps,
estimated-vs-actual delivery differences, and any feature derived from the
outcome must not be used as inputs.

### Customer dissatisfaction

Proposed target:

`is_dissatisfied = review_score in {1, 2}`

The prediction point is before review submission. Review score, review text,
review creation/answer dates, and post-review information must not be used as
inputs. Actual delivery outcomes are also excluded when they would not be
available at the intended prediction point.

These definitions remain subject to the actual schema, missingness, join
cardinality, and timestamp checks produced by the Phase 1 inspection.
