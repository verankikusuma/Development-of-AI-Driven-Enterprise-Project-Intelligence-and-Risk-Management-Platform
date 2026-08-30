import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_project_risk.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_project():
    payload = {
        "name": "Test Metro Railway",
        "description": "Integration test line",
        "deadline": "2026-08-15T00:00:00",
        "budget": 50000000.0,
        "current_budget_used": 20000000.0,
        "status": "IN_PROGRESS"
    }
    res = client.post("/api/projects", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Test Metro Railway"
    p_id = data["id"]

    # Get project
    res_get = client.get(f"/api/projects/{p_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == p_id

def test_task_creation_and_impact():
    # 1. Create project
    p_res = client.post("/api/projects", json={
        "name": "Driverless System",
        "deadline": "2026-08-15T00:00:00"
    })
    p_id = p_res.json()["id"]

    # 2. Create Task 1 (Sensors)
    t1_res = client.post(f"/api/projects/{p_id}/tasks", json={
        "name": "LiDAR Sensor Array",
        "team": "Sensors",
        "planned_end_date": "2026-08-01T00:00:00",
        "delay_days": 4,
        "progress_percentage": 50.0
    })
    t1_id = t1_res.json()["id"]

    # 3. Create Task 2 (AI Testing)
    t2_res = client.post(f"/api/projects/{p_id}/tasks", json={
        "name": "Autonomous AI Verification",
        "team": "AI Software",
        "planned_end_date": "2026-08-10T00:00:00",
        "delay_days": 0,
        "progress_percentage": 20.0
    })
    t2_id = t2_res.json()["id"]

    # 4. Create Dependency
    dep_res = client.post(f"/api/projects/{p_id}/dependencies", json={
        "source_task_id": t1_id,
        "dependent_task_id": t2_id,
        "dependency_strength": 1.0
    })
    assert dep_res.status_code == 200

    # 5. Check Dependency Impact
    imp_res = client.get(f"/api/tasks/{t1_id}/dependency-impact")
    assert imp_res.status_code == 200
    impact = imp_res.json()
    assert impact["task_id"] == t1_id
    assert len(impact["direct_dependents"]) == 1
    assert impact["direct_dependents"][0]["id"] == t2_id
