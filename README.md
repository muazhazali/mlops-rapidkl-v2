# Malaysia Public Transport MLOps

An end-to-end MLOps project using public transport ridership data from **data.gov.my**.

py -m venv .venv
 .\.venv\Scripts\Activate.ps1

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

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
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