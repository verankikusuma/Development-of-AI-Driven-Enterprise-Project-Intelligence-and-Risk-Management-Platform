from typing import List, Any, Dict
import numpy as np

def calculate_project_health(
    project: Any,
    tasks: List[Any],
    dependencies: List[Any],
    risk_prob: float,
    metrics: Any = None
) -> Dict[str, Any]:
    """
    Computes an objective multi-criteria project health index (0 to 100).
    Combines:
    - Schedule Health (30%)
    - Risk Inversion Health (25%)
    - Testing & Safety Health (20%)
    - Resource Health (15%)
    - Budget Health (10%)
    """
    total_tasks = len(tasks) if tasks else 1
    
    # 1. Schedule Health (based on delays vs total duration)
    total_delay = sum(getattr(t, "delay_days", 0) for t in tasks)
    delayed_count = sum(1 for t in tasks if getattr(t, "delay_days", 0) > 0)
    schedule_health = max(10.0, 100.0 - (total_delay * 3.5) - (delayed_count * 5.0))
    
    # 2. Risk Inversion Health
    risk_health = max(5.0, (1.0 - risk_prob) * 100.0)
    
    # 3. Testing Health
    testing_tasks = [t for t in tasks if "test" in getattr(t, "name", "").lower() or "safety" in getattr(t, "name", "").lower()]
    if testing_tasks:
        test_progress = float(np.mean([t.progress_percentage for t in testing_tasks]))
        test_delays = sum(t.delay_days for t in testing_tasks)
        testing_health = max(10.0, test_progress - (test_delays * 4.0))
    else:
        testing_health = 65.0
        
    # 4. Resource Health
    avg_res = float(np.mean([getattr(t, "resource_availability", 1.0) for t in tasks])) if tasks else 1.0
    resource_health = max(10.0, avg_res * 100.0)
    
    # 5. Budget Health
    if project.budget > 0:
        util = project.current_budget_used / project.budget
        budget_health = max(10.0, 100.0 - max(0.0, (util - 1.0) * 120.0))
    else:
        budget_health = 85.0
        
    # 6. Dependency Health
    critical_dep_count = sum(1 for d in dependencies if getattr(d, "dependency_strength", 1.0) >= 0.8)
    dep_health = max(15.0, 100.0 - (total_delay * 2.0) - (critical_dep_count * 4.0))
    
    # Overall Composite Score
    overall_score = (
        0.30 * schedule_health
        + 0.25 * risk_health
        + 0.20 * testing_health
        + 0.15 * resource_health
        + 0.10 * budget_health
    )
    overall_score = round(max(5.0, min(98.0, overall_score)), 1)
    
    if overall_score >= 80.0:
        health_status = "EXCELLENT"
        summary = "Project is tracking smoothly with low schedule slippage and healthy safety margins."
    elif overall_score >= 60.0:
        health_status = "GOOD"
        summary = "Project performance is stable, with minor isolated delays being actively monitored."
    elif overall_score >= 40.0:
        health_status = "AT_RISK"
        summary = "Upstream task bottlenecks and testing lags present clear risks to the August 15 launch target."
    else:
        health_status = "CRITICAL"
        summary = "Severe cascade delays detected on the critical path. Immediate corrective allocation required."

    risk_level = "LOW" if risk_prob < 0.3 else "MEDIUM" if risk_prob < 0.55 else "HIGH" if risk_prob < 0.75 else "CRITICAL"

    return {
        "project_id": project.id,
        "overall_health_score": overall_score,
        "health_status": health_status,
        "risk_probability": round(risk_prob, 4),
        "risk_level": risk_level,
        "schedule_health": round(schedule_health, 1),
        "budget_health": round(budget_health, 1),
        "resource_health": round(resource_health, 1),
        "testing_health": round(testing_health, 1),
        "dependency_health": round(dep_health, 1),
        "summary_message": summary,
        "calculation_method": "Multi-criteria weighted index evaluated alongside ML probability"
    }
