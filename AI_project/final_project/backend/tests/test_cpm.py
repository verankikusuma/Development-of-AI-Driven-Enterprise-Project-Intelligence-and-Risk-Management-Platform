import pytest
from app.services.cpm_service import calculate_critical_path
from app.services.dependency_service import analyze_task_dependency_impact

class MockTask:
    def __init__(self, id, name, team="Team A", delay_days=0, remaining_duration=10, progress_percentage=50.0, status="IN_PROGRESS"):
        self.id = id
        self.name = name
        self.team = team
        self.delay_days = delay_days
        self.estimated_duration = remaining_duration
        self.remaining_duration = remaining_duration
        self.progress_percentage = progress_percentage
        self.status = status

class MockDep:
    def __init__(self, id, source_task_id, dependent_task_id, strength=1.0, dependency_type="FINISH_TO_START"):
        self.id = id
        self.source_task_id = source_task_id
        self.dependent_task_id = dependent_task_id
        self.dependency_strength = strength
        self.dependency_type = dependency_type

def test_cpm_linear_chain():
    # A (10d) -> B (5d) -> C (15d)
    t1 = MockTask(1, "A", remaining_duration=10)
    t2 = MockTask(2, "B", remaining_duration=5)
    t3 = MockTask(3, "C", remaining_duration=15)
    
    deps = [
        MockDep(1, 1, 2),
        MockDep(2, 2, 3)
    ]
    
    res = calculate_critical_path([t1, t2, t3], deps)
    assert res["project_duration_days"] == 30
    assert set(res["critical_task_ids"]) == {1, 2, 3}

def test_dependency_cascade_impact():
    # Sensor (1) -> AI (2) -> Safety (3) -> Launch (4)
    t1 = MockTask(1, "Sensor Installation", delay_days=5)
    t2 = MockTask(2, "AI Testing", delay_days=0)
    t3 = MockTask(3, "Safety Testing", delay_days=0)
    t4 = MockTask(4, "Launch", delay_days=0)
    
    deps = [
        MockDep(1, 1, 2),
        MockDep(2, 2, 3),
        MockDep(3, 3, 4)
    ]
    
    impact = analyze_task_dependency_impact(1, [t1, t2, t3, t4], deps)
    assert impact["task_id"] == 1
    assert len(impact["direct_dependents"]) == 1
    assert len(impact["downstream_tasks"]) == 3
    assert impact["dependency_depth"] == 3
    assert impact["cascade_chain"] == ["Sensor Installation", "AI Testing", "Safety Testing", "Launch"]
