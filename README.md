# Malaysia Public Transport MLOps

An end-to-end MLOps project using public transport ridership data from **data.gov.my**.

## Development Setup

<details>
<summary><strong>Recommended: Set up an existing clone with <code>uv sync</code></strong></summary>

Install `uv` if it is not already available:

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal, clone the repository, and install the locked dependencies:

```bash
git clone <repository-url>
cd mlops-rapidkl-v2
uv sync --extra model --extra api --extra dev
```

`uv sync` creates `.venv` automatically and installs the versions recorded in
`uv.lock`. Activation is optional when commands are run with `uv run`.

To use `notebooks/01_eda.ipynb` in VS Code, select the interpreter at
`.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Linux/macOS.

</details>

<details>
<summary><strong>Set up a new <code>uv</code> project from scratch</strong></summary>

Install `uv` using one of the commands above, then initialize the project and
add its dependencies:

```bash
uv init
uv add pandas pyarrow matplotlib seaborn jupyter h2o
uv sync
```

To activate the virtual environment manually:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Commit `pyproject.toml`, `uv.lock`, and `.python-version` so other users can
reproduce the environment with `uv sync`. Do not commit `.venv`.

</details>

## Goal

Predict future public transport ridership while learning:

* Machine Learning
* MLflow
* FastAPI
* Podman/Docker
* GitHub Actions CI/CD
* Model monitoring

## Architecture

```text
data.gov.my
   ↓
Data Ingestion
   ↓
Validation
   ↓
Feature Engineering
   ↓
XGBoost
   ↓
MLflow
   ↓
FastAPI
   ↓
Podman
   ↓
Proxmox LXC
   ↓
Cloudflare Tunnel
```

## Stack

* Python
* Pandas
* XGBoost
* MLflow
* FastAPI
* PostgreSQL
* Podman
* GitHub Actions
* Proxmox
* Cloudflare Tunnel

## Project Structure

```text
mlops-rapidkl-v2/
├── src/                    # rapidkl package (config, data, features, train, predict)
│   ├── __init__.py
│   ├── config.py           # TARGET, FEATURE_COLUMNS, split dates, paths
│   ├── data.py             # load parquet/CSV
│   ├── validate.py         # schema & quality assertions
│   ├── features.py         # calendar, holiday, lag, rolling features
│   ├── dataset.py          # train/val/test splits, X/y
│   ├── metrics.py          # MAE, RMSE, WMAPE
│   ├── train.py            # XGBoost + MLflow tracking
│   └── predict.py          # load/predict from MLflow registry
├── api/                    # FastAPI service
│   ├── __init__.py
│   ├── main.py             # /health, /predict endpoints
│   ├── schemas.py          # Pydantic request/response models
│   ├── loader.py           # cached MLflow model loading
│   └── features_service.py # build features for a future date
├── tests/                  # pytest suite (data, features, predict, API)
├── data/                   # ridership parquet + CSV
├── notebooks/              # EDA + model experiments
├── .github/workflows/
│   └── ci.yml               # lint + test on push/PR
├── Containerfile           # Podman/Docker image (uv-based)
├── compose.yml              # api + mlflow + postgres
├── pyproject.toml
└── uv.lock
```

## Development

Run commands inside the managed environment without activating it:

```bash
uv run <command>
```

Install all optional dependencies (model, api, dev):

```bash
uv sync --extra model --extra api --extra dev
```

Train the model (logs to MLflow, registers with Production alias):

```bash
uv run python -c "from rapidkl.train import train_model; r = train_model(); print(r['val_metrics'], r['test_metrics'])"
```

Run tests:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check src/ api/ tests/
```

Run API locally:

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Predict via API:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"target_date": "2026-07-01", "target": "rail_mrt_kajang"}'
```

Start services (api + mlflow + postgres):

```bash
podman compose up -d
```

## CI/CD

```text
git push
   ↓
GitHub Actions
   ↓
Lint (ruff) + Tests (pytest)
   ↓
Build Container
   ↓
Deploy to Proxmox (TODO)
```

## Future Improvements

* Automated retraining
* Model promotion
* Data/model drift monitoring
* Grafana dashboard
* k3s/Kubernetes deployment

Source: https://data.gov.my/data-catalogue/ridership_headline?visual=table
