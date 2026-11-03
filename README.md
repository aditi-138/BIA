# E-Commerce Delivery Delay & Customer Dissatisfaction Risk Analytics

Integrated machine learning framework using the **Olist Brazilian E-Commerce Public Dataset** for:

1. **Delivery delay prediction** (binary classification)
2. **Customer dissatisfaction prediction** (review score 1–2 vs other)
3. **Integrated order-level risk engine** and a **Streamlit** demonstration app

This repository is developed **phase by phase**. Later phases are not started until the current phase is explicitly approved.

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
│   └── verify_environment.py  # Phase 0 environment check
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

---

## How to run the Streamlit application (Phase 7)

The application is **not** implemented in Phase 0. After Phase 7:

```powershell
streamlit run app/app.py
```

The app must load saved Joblib models from `models/`; it must not retrain at startup.

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
| 0 | Project planning and environment setup | Approved |
| 1 | Dataset inspection and business understanding | **Current** |
| 2 | Data cleaning and feature engineering | Not started |
| 3 | Exploratory data analysis | Not started |
| 4 | Delivery delay prediction model | Not started |
| 5 | Customer dissatisfaction prediction model | Not started |
| 6 | Integrated risk engine | Not started |
| 7 | Interactive Streamlit application | Not started |
| 8 | Testing, final evaluation and documentation | Not started |

---

## Academic integrity

- Do not invent metrics, probabilities or business impact claims.
- Associations from models are not causal explanations.
- Document limitations of historical Olist data clearly in later phases.
