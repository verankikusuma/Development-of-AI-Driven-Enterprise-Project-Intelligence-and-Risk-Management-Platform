# AI Project Risk Forecasting System - Backend Service

FastAPI-powered machine learning and dependency risk forecasting engine for mission-critical project management.

## Features

- **ML Risk Forecasting**: Scikit-learn predictive model outputting true probabilistic risk `[0.0 - 1.0]` and categorical bands (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **17 Engineered Features**: Zero data-leakage telemetry representation capturing progress velocity, resource deficit, bug density, testing failure rates, and upstream dependency delays.
- **Topological Dependency Graph**: NetworkX directed acyclic graph (DAG) calculating downstream cascade depth, affected work packages, and ripple effects.
- **Critical Path Method (CPM)**: Computes Forward Pass (Early Start, Early Finish), Backward Pass (Late Start, Late Finish), and Total Float slack.
- **What-If Scenario Simulation**: Injects schedule delays or resource shocks into specific tasks and recalculates simulated risk delta across the network.
- **Prescriptive Preventive Actions**: Rule-informed, prioritized mitigation actions addressing root-cause bottlenecks.

## Quickstart

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Database Migrations & Seeding
```bash
# Apply schema
alembic upgrade head

# Generate synthetic dataset & train ML risk model
python scripts/generate_training_data.py
python -m app.ml.train

# Seed India Driverless Metro Launch baseline data
python scripts/seed.py
```

### 3. Launch Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Running Automated Tests
```bash
pytest
```

## Docker Deployment
```bash
docker compose up --build
```
