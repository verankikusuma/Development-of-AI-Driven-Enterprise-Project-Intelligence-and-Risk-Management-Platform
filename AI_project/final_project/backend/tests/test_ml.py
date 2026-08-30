import pytest
from app.ml.feature_extractor import FEATURE_NAMES, extract_features_from_project_state
from app.ml.synthetic_data import generate_synthetic_dataset
from app.ml.predict import predict_project_risk

class MockTask:
    def __init__(self, id, name, delay_days=0, progress_percentage=50.0, resource_availability=0.8, bugs_reported=2, requirement_changes=1, status="IN_PROGRESS"):
        self.id = id
        self.name = name
        self.delay_days = delay_days
        self.progress_percentage = progress_percentage
        self.resource_availability = resource_availability
        self.bugs_reported = bugs_reported
        self.requirement_changes = requirement_changes
        self.status = status

class MockDependency:
    def __init__(self, source_task_id, dependent_task_id, strength=1.0):
        self.source_task_id = source_task_id
        self.dependent_task_id = dependent_task_id
        self.dependency_strength = strength

def test_feature_extractor_completeness():
    tasks = [
        MockTask(1, "Sensor Installation", delay_days=5, progress_percentage=60.0),
        MockTask(2, "AI Safety Testing", delay_days=2, progress_percentage=40.0)
    ]
    deps = [MockDependency(1, 2, 1.0)]
    
    features = extract_features_from_project_state(tasks, deps)
    for name in FEATURE_NAMES:
        assert name in features
        assert isinstance(features[name], (int, float))

def test_synthetic_data_properties():
    df = generate_synthetic_dataset(num_samples=100, random_seed=42)
    assert len(df) == 100
    for name in FEATURE_NAMES:
        assert name in df.columns
    assert "true_risk_probability" in df.columns
    assert "risk_level" in df.columns
    assert df["true_risk_probability"].min() >= 0.0
    assert df["true_risk_probability"].max() <= 1.0

def test_risk_prediction_output_bounds():
    features = {name: 0.5 for name in FEATURE_NAMES}
    features["delay_days"] = 10.0
    features["dependency_delay"] = 15.0
    
    prob, level, factors = predict_project_risk(features)
    assert 0.0 <= prob <= 1.0
    assert level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(factors) > 0
