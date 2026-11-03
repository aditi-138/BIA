# Service Recovery Intelligence

**Business Intelligence and Analytics decision-support system for fulfillment exceptions and customer experience.**

This project develops a commercial-style **Service Recovery Intelligence** workspace using the **Olist Brazilian E-Commerce Public Dataset** as an operational case dataset for:

1. monitoring confirmed fulfillment outcomes;
2. estimating late-delivery likelihood;
3. estimating low-review likelihood from pre-review order information;
4. prioritising intervention through a combined risk policy;
5. presenting model governance and decision-support views in Streamlit.

The detailed academic and business framing is documented in
[`BIa/docs/problem_statement.md`](BIa/docs/problem_statement.md).

This repository is developed as a complete, reproducible Business Intelligence and Analytics case study. The current branch contains the prepared data pipeline, trained artifacts, decision-support policy, Streamlit application, tests, and faculty demonstration documentation.

---

## Project structure

```text
BIa/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── config.py              # Seeds, paths, prediction points, targets
├── data/
│   ├── raw/                   # Place Olist CSVs here (not committed)
│   ├── interim/
│   ├── processed/
│   └── external/
├── notebooks/                 # Phase notebooks (from Phase 1)
├── scripts/
│   └── inspect_dataset.py     # Phase 1 dataset inspection
├── src/                       # Reusable Python modules
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── risk/
│   └── visualization/
├── models/                    # Saved Joblib artefacts (from Phase 4+)
├── reports/
│   └── figures/
├── app/                       # Streamlit application (Phase 7)
├── tests/
└── docs/
    ├── project_specification.md
    ├── dataset_inventory.md          # Phase 1
    ├── data_dictionary.md            # Phase 1
    ├── data_quality_report.md        # Phase 1
    └── target_definitions.md         # Phase 1
```

---

## Environment setup

### 1. Prerequisites

- Python **3.11+** (verified during Phase 0 on this machine: 3.11.9)
- `pip`
- Optional: [Git](https://git-scm.com/), [Kaggle account](https://www.kaggle.com/) for dataset download

### 2. Create a virtual environment (recommended)

From the project root (`BIa/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Register a Jupyter kernel (optional but useful)

```powershell
python -m ipykernel install --user --name bia-olist --display-name "Python (BIa Olist)"
```

### 4. Verify configuration

```powershell
python config\config.py
```

This prints the project root, random seed (`42`), prediction points, and which Olist CSVs are still missing from `data/raw/`.

---

## How to obtain the Olist dataset

Official source: [Kaggle — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

### Option A — Manual download (simplest if Kaggle CLI is not installed)

1. Sign in to Kaggle.
2. Open the dataset page above.
3. Click **Download**.
4. Unzip the archive.
5. Copy **all** CSV files into:

```text
data/raw/
```

Expected filenames (also listed in `config/config.py`):

| File | Role |
|------|------|
| `olist_orders_dataset.csv` | Order lifecycle timestamps and status |
| `olist_order_items_dataset.csv` | Items, sellers, prices, shipping |
| `olist_order_payments_dataset.csv` | Payment type and value |
| `olist_order_reviews_dataset.csv` | Review scores and text |
| `olist_customers_dataset.csv` | Customer and location keys |
| `olist_products_dataset.csv` | Product attributes |
| `olist_sellers_dataset.csv` | Seller locations |
| `olist_geolocation_dataset.csv` | Zip-code geolocation |
| `product_category_name_translation.csv` | Category EN translation |

### Option B — Kaggle CLI

1. Create a Kaggle API token: Account → Settings → API → Create New Token (`kaggle.json`).
2. Place it where the Kaggle CLI expects it (Windows typical path: `C:\Users\<You>\.kaggle\kaggle.json`).
3. Run:

```powershell
pip install kaggle
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

### Confirm files are present

```powershell
python config\config.py
```

You should see: `All expected Olist raw CSV files are present in data/raw.`

**Phase 0 note:** As of setup, the dataset was **not** found locally and the Kaggle CLI was **not** installed. Phase 1 requires these CSVs.

---

## How to run notebooks

After installing requirements and placing data in `data/raw/`:

```powershell
python -m notebook
```

Or open the project in Cursor / VS Code and run notebooks under `notebooks/` with the project virtual environment selected.

Recommended order (after each phase is approved):

1. `01_data_understanding.ipynb`
2. `02_data_preparation.ipynb`
3. `03_exploratory_analysis.ipynb`
4. `04_delivery_delay_model.ipynb`
5. `05_dissatisfaction_model.ipynb`
6. `06_integrated_risk_engine.ipynb`

For the current Phase 1 inspection utility and its focused tests:

```powershell
python BIa\scripts\inspect_dataset.py --output BIa\data\interim\dataset_inventory.json
python -m unittest discover -s BIa\tests -p "test_*.py" -v
```

The inspection command exits with code `2` while expected source files are
missing. That is an intentional data-readiness guard, not a model failure.

---

## How to run the Streamlit application

```powershell
python -m streamlit run BIa\app\app.py
```

The app loads saved Joblib models from `BIa\models\`; it does not retrain at startup.
For the recommended five-minute walkthrough, see
[`BIa/docs/faculty_demo_script.md`](BIa/docs/faculty_demo_script.md).

---

## Reproducibility

| Setting | Value |
|---------|-------|
| Random seed | `42` |
| Config module | `config/config.py` |
| Delay prediction point | `order_approved_at` |
| Dissatisfaction prediction point | `pre_review_submission` |

Full scope, leakage rules and phase gates: [`docs/project_specification.md`](docs/project_specification.md).

---

## Phase status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project planning and environment setup | Complete |
| 1 | Dataset inspection and business understanding | Complete |
| 2 | Data cleaning and feature engineering | Complete |
| 3 | Exploratory analysis and outcome profiling | Complete |
| 4 | Delivery delay prediction model | Complete; weak test discrimination documented |
| 5 | Customer dissatisfaction prediction model | Complete |
| 6 | Integrated risk engine | Complete |
| 7 | Interactive Streamlit application | Complete |
| 8 | Testing, final evaluation and documentation | Complete |

---

## Academic integrity

- Do not invent metrics, probabilities or business impact claims.
- Associations from models are not causal explanations.
- Document limitations of historical Olist data clearly in later phases.
