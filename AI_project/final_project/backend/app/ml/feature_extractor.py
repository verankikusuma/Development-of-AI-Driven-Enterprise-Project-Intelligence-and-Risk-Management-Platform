from typing import List, Dict, Any
import numpy as np

FEATURE_NAMES = [
    "progress_percentage",
    "pending_task_ratio",
    "delay_days",
    "budget_utilization",
    "resource_availability",
    "bugs_per_task",
    "testing_progress",
    "testing_failure_rate",
    "requirement_change_rate",
    "team_productivity",
    "dependency_delay",
    "critical_dependency_count",
    "security_audit_progress",
    "external_risk_score",
    "schedule_variance",
    "resource_pressure",
    "dependency_risk_score"
]

def extract_features_from_project_state(
    tasks: List[Any],
    dependencies: List[Any],
    latest_metrics: Any = None,
    critical_path_info: Dict[str, Any] = None
) -> Dict[str, float]:
    """
    Extracts 17 non-leaking ML features from the project state at the current moment.
    """
    total_tasks = len(tasks) if tasks else 1
    
    # Task level statistics
    total_progress = sum(getattr(t, "progress_percentage", 0.0) for t in tasks)
    avg_progress = total_progress / total_tasks
    
    pending_tasks = sum(1 for t in tasks if getattr(t, "status", "") in ["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "DELAYED"])
    pending_ratio = pending_tasks / total_tasks
    
    total_delay = sum(getattr(t, "delay_days", 0) for t in tasks)
    total_bugs = sum(getattr(t, "bugs_reported", 0) for t in tasks)
    bugs_per_task = total_bugs / total_tasks
    
    req_changes = sum(getattr(t, "requirement_changes", 0) for t in tasks)
    requirement_change_rate = req_changes / total_tasks
    
    avg_resource_avail = float(np.mean([getattr(t, "resource_availability", 1.0) for t in tasks])) if tasks else 1.0
    
    # Testing specific metrics
    testing_tasks = [t for t in tasks if "test" in getattr(t, "name", "").lower() or "safety" in getattr(t, "name", "").lower() or "audit" in getattr(t, "name", "").lower()]
    if testing_tasks:
        testing_progress = float(np.mean([getattr(t, "progress_percentage", 0.0) for t in testing_tasks]))
    elif latest_metrics and hasattr(latest_metrics, "testing_progress"):
        testing_progress = float(latest_metrics.testing_progress)
    else:
        testing_progress = avg_progress
        
    testing_failures = getattr(latest_metrics, "testing_failures", 0) if latest_metrics else 0
    testing_failure_rate = min(1.0, testing_failures / (max(1, total_bugs + testing_failures)))
    
    # Security progress
    sec_tasks = [t for t in tasks if "security" in getattr(t, "name", "").lower() or "cyber" in getattr(t, "name", "").lower()]
    if sec_tasks:
        security_audit_progress = float(sec_tasks[0].progress_percentage)
    elif latest_metrics and hasattr(latest_metrics, "security_audit_progress"):
        security_audit_progress = float(latest_metrics.security_audit_progress)
    else:
        security_audit_progress = avg_progress
        
    # Budget and external
    budget_utilization = getattr(latest_metrics, "budget_utilization", 0.5) if latest_metrics else 0.5
    team_productivity = getattr(latest_metrics, "team_productivity", 1.0) if latest_metrics else 1.0
    external_risk_score = getattr(latest_metrics, "external_risk", 0.3) if latest_metrics else 0.3
    schedule_variance = getattr(latest_metrics, "schedule_variance", float(total_delay / max(1, total_tasks))) if latest_metrics else float(total_delay / max(1, total_tasks))
    
    # Dependencies analysis
    total_dep_delay = 0
    task_map = {t.id: t for t in tasks} if hasattr(tasks[0], "id") else {}
    critical_deps = 0
    
    for dep in dependencies:
        source_id = getattr(dep, "source_task_id", None)
        strength = getattr(dep, "dependency_strength", 1.0)
        if strength >= 0.8:
            critical_deps += 1
        if source_id in task_map:
            src_task = task_map[source_id]
            if getattr(src_task, "delay_days", 0) > 0:
                total_dep_delay += int(src_task.delay_days * strength)
                
    # Derived composite features
    resource_pressure = max(0.0, min(1.0, (1.0 - avg_resource_avail) * 1.5 + (pending_ratio * 0.5)))
    dependency_risk_score = min(1.0, (total_dep_delay * 0.05) + (critical_deps * 0.08))
    
    features = {
        "progress_percentage": round(float(avg_progress), 2),
        "pending_task_ratio": round(float(pending_ratio), 4),
        "delay_days": float(total_delay),
        "budget_utilization": round(float(budget_utilization), 4),
        "resource_availability": round(float(avg_resource_avail), 4),
        "bugs_per_task": round(float(bugs_per_task), 3),
        "testing_progress": round(float(testing_progress), 2),
        "testing_failure_rate": round(float(testing_failure_rate), 4),
        "requirement_change_rate": round(float(requirement_change_rate), 4),
        "team_productivity": round(float(team_productivity), 3),
        "dependency_delay": float(total_dep_delay),
        "critical_dependency_count": float(critical_deps),
        "security_audit_progress": round(float(security_audit_progress), 2),
        "external_risk_score": round(float(external_risk_score), 4),
        "schedule_variance": round(float(schedule_variance), 2),
        "resource_pressure": round(float(resource_pressure), 4),
        "dependency_risk_score": round(float(dependency_risk_score), 4)
    }
    
    return features
