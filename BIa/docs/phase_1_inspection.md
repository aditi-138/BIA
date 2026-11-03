# Phase 1 — Dataset Inspection

## Purpose

Phase 1 establishes whether the official Olist tables can support the two
planned targets without guessing about schema, joins, timestamps, or leakage.
It must finish before feature engineering or model training begins.

## Run the inspection

From the repository root:

```powershell
python BIa\scripts\inspect_dataset.py --output BIa\data\interim\dataset_inventory.json
```

To produce both machine-readable and human-readable outputs:

```powershell
python BIa\scripts\inspect_dataset.py `
  --output BIa\data\interim\dataset_inventory.json `
  --markdown-output BIa\docs\dataset_inventory.md
```

The command inspects every expected CSV that exists and reports missing files
explicitly. It exits with code `2` while any expected file is missing. This is
intentional: a partial inventory is useful for setup diagnostics, but it is
not evidence that Phase 1 is complete.

After all nine official CSVs are present, rerun the command and review:

- dimensions and column names;
- inferred data types;
- missing-value counts;
- duplicate rows;
- key-column completeness and uniqueness;
- timestamp validity and ranges.
- required-column checks and target-readiness flags;
- documented relationship metadata for safe joins.

`BIa/docs/data_dictionary.md` records the intended table roles, modelling
grain, relationship assumptions, target definitions, and leakage exclusions.
The generated `dataset_inventory.md` contains only observations from files
actually found on disk.

## Current observed results

The current complete-data run reports 99,441 orders, 96,476 delivery-delay
eligible rows with 7,827 delayed orders (8.1129%), and 99,224 review rows with
14,575 dissatisfied reviews (14.6890%). Core order, item, payment, review,
customer, product, and seller references have full coverage. Thirteen product
category values have no translation; this is a label-coverage limitation, not
a reason to discard the products.

## Required Phase 1 conclusions

The completed Phase 1 deliverable must use the generated evidence to document:

1. relationships among orders, customers, items, payments, reviews, products,
   sellers, geolocation, and category translation;
2. the order-level modelling grain and safe join rules;
3. the delivery-delay target and dissatisfaction target feasibility;
4. columns that are unavailable at each prediction point or would leak the
   outcome;
5. timestamp coverage, incomplete records, duplicate keys, and other data
   limitations.

No target prevalence, model metric, prediction probability, or business
finding should be written until the relevant tables have been inspected.

The JSON report includes `target_readiness` flags. These flags are setup
guards, not model results: they remain false when required files or columns
are unavailable.

## Run focused tests

```powershell
python -m unittest discover -s BIa\tests -p "test_*.py" -v
```
