# Dataset Inventory

Generated from the locally available files; missing inputs are not inferred.

## Readiness

- Expected files: 9
- Available files: 9
- Missing files: 0
- `complete_raw_dataset`: ready
- `required_columns_present`: ready
- `delivery_delay_target_ready`: ready
- `dissatisfaction_target_ready`: ready

## File inventory

| Table | Status | Rows | Columns | Duplicate rows |
|---|---|---:|---:|---:|
| `orders` | Inspected | 99441 | 8 | 0 |
| `order_items` | Inspected | 112650 | 7 | 0 |
| `order_payments` | Inspected | 103886 | 5 | 0 |
| `order_reviews` | Inspected | 99224 | 7 | 0 |
| `customers` | Inspected | 99441 | 5 | 0 |
| `products` | Inspected | 32951 | 9 | 0 |
| `sellers` | Inspected | 3095 | 4 | 0 |
| `geolocation` | Inspected | 1000163 | 5 | 261831 |
| `category_translation` | Inspected | 71 | 2 | 0 |

## Declared relationships

| From | To | Cardinality |
|---|---|---|
| `orders.customer_id` | `customers.customer_id` | many-to-one |
| `order_items.order_id` | `orders.order_id` | many-to-one |
| `order_items.product_id` | `products.product_id` | many-to-one |
| `order_items.seller_id` | `sellers.seller_id` | many-to-one |
| `order_payments.order_id` | `orders.order_id` | many-to-one |
| `order_reviews.order_id` | `orders.order_id` | many-to-one |
| `products.product_category_name` | `category_translation.product_category_name` | many-to-one |
