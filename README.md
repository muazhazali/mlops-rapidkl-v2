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
uv sync
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
transport-mlops/
├── src/
├── api/
├── tests/
├── data/
├── models/
├── notebooks/
├── Containerfile
├── compose.yml
└── requirements.txt
```

## Development

Run commands inside the managed environment without activating it:

```bash
uv run <command>
```

Run tests:

```bash
pytest
```

Run API:

```bash
uvicorn api.main:app --reload --port 8000
```

Start services:

```bash
podman compose up -d
```

## CI/CD

```text
git push
   ↓
GitHub Actions
   ↓
Lint + Tests
   ↓
Build Container
   ↓
Deploy to Proxmox
```

## Future Improvements

* Automated retraining
* Model promotion
* Data/model drift monitoring
* Grafana dashboard
* k3s/Kubernetes deployment

Source: https://data.gov.my/data-catalogue/ridership_headline?visual=table
