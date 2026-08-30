from typing import List, Dict, Any
import copy
from datetime import datetime, timedelta
from app.services.dependency_service import build_dependency_graph, analyze_task_dependency_impact
from app.services.cpm_service import calculate_critical_path
from app.ml.feature_extractor import extract_features_from_project_state
from app.ml.predict import predict_project_risk
import networkx as nx

def simulate_what_if_scenario(
    project: Any,
    tasks: List[Any],
    dependencies: List[Any],
    task_id: int,
    additional_delay_days: int,
    resource_reduction_percent: float = 0.0
) -> Dict[str, Any]:
    """
    Executes a What-If Scenario simulation by injecting hypothetical delay into a task,
    propagating the delay downstream through the DAG, extracting new ML features, and
    computing the delta risk increase.
    """
    # 1. Base prediction
    base_features = extract_features_from_project_state(tasks, dependencies)
    current_risk_prob, current_level, _ = predict_project_risk(base_features)
    
    # 2. Clone tasks and apply simulation
    task_map = {t.id: copy.copy(t) for t in tasks}
    if task_id not in task_map:
        raise ValueError(f"Task with ID {task_id} does not exist.")
        
    target_task = task_map[task_id]
    target_task.delay_days = target_task.delay_days + additional_delay_days
    if resource_reduction_percent > 0:
        target_task.resource_availability = max(0.2, target_task.resource_availability * (1.0 - resource_reduction_percent / 100.0))
        
    # 3. Propagate delay downstream using NetworkX DAG
    G = build_dependency_graph(tasks, dependencies)
    descendants = list(nx.descendants(G, task_id)) if task_id in G else []
    
    affected_tasks = []
    # Topological propagation
    for desc_id in descendants:
        if desc_id in task_map:
            d_task = task_map[desc_id]
            # Downstream slip calculation
            inherited_slip = int(round(additional_delay_days * 0.8))
            d_task.delay_days = d_task.delay_days + inherited_slip
            affected_tasks.append({
                "id": d_task.id,
                "name": d_task.name,
                "team": d_task.team,
                "inherited_delay_days": inherited_slip,
                "total_simulated_delay": d_task.delay_days
            })
            
    simulated_tasks_list = list(task_map.values())
    
    # 4. Extract simulated features and run ML inference
    simulated_features = extract_features_from_project_state(simulated_tasks_list, dependencies)
    scenario_risk_prob, scenario_level, _ = predict_project_risk(simulated_features)
    
    risk_increase = round(max(0.0, (scenario_risk_prob - current_risk_prob) * 100.0), 1)
    
    # Schedule impact
    estimated_schedule_impact = additional_delay_days + (len(descendants) > 0 and int(additional_delay_days * 0.4) or 0)
    base_deadline = project.deadline
    if isinstance(base_deadline, str):
        base_deadline = datetime.fromisoformat(base_deadline.replace("Z", "+00:00"))
    forecast_sim_date = base_deadline + timedelta(days=target_task.delay_days + estimated_schedule_impact)
    
    return {
        "project_id": project.id,
        "simulated_task_id": target_task.id,
        "simulated_task_name": target_task.name,
        "simulated_delay_days": additional_delay_days,
        "current_risk_probability": round(current_risk_prob, 4),
        "scenario_risk_probability": round(scenario_risk_prob, 4),
        "risk_increase_percentage": risk_increase,
        "affected_tasks_count": len(affected_tasks),
        "affected_tasks": affected_tasks,
        "estimated_schedule_impact_days": estimated_schedule_impact,
        "forecast_completion_date": forecast_sim_date.strftime("%Y-%m-%d"),
        "disclaimer": "Scenario Simulation — not a guaranteed future outcome."
    }
