import networkx as nx
from typing import List, Dict, Any, Tuple

def build_dependency_graph(tasks: List[Any], dependencies: List[Any]) -> nx.DiGraph:
    """
    Constructs a directed graph representing task workflow dependencies.
    """
    G = nx.DiGraph()
    
    for task in tasks:
        G.add_node(
            task.id,
            id=task.id,
            name=task.name,
            team=task.team,
            status=task.status,
            progress=task.progress_percentage,
            delay_days=task.delay_days,
            estimated_duration=task.estimated_duration,
            remaining_duration=task.remaining_duration
        )
        
    for dep in dependencies:
        G.add_edge(
            dep.source_task_id,
            dep.dependent_task_id,
            id=dep.id,
            dependency_type=dep.dependency_type,
            strength=dep.dependency_strength
        )
        
    return G

def analyze_task_dependency_impact(
    task_id: int,
    tasks: List[Any],
    dependencies: List[Any]
) -> Dict[str, Any]:
    """
    Analyzes downstream cascade impact of a specific task using NetworkX.
    """
    G = build_dependency_graph(tasks, dependencies)
    task_map = {t.id: t for t in tasks}
    
    target_task = task_map.get(task_id)
    if not target_task:
        raise ValueError(f"Task {task_id} not found")
        
    # Direct successors
    direct_successors = list(G.successors(task_id)) if task_id in G else []
    direct_dependents = []
    for s_id in direct_successors:
        if s_id in task_map:
            s_task = task_map[s_id]
            direct_dependents.append({
                "id": s_task.id,
                "name": s_task.name,
                "team": s_task.team,
                "status": s_task.status,
                "progress": s_task.progress_percentage
            })
            
    # All downstream descendants
    descendants = list(nx.descendants(G, task_id)) if task_id in G else []
    downstream_tasks = []
    for d_id in descendants:
        if d_id in task_map:
            d_task = task_map[d_id]
            downstream_tasks.append({
                "id": d_task.id,
                "name": d_task.name,
                "team": d_task.team,
                "status": d_task.status,
                "progress": d_task.progress_percentage,
                "delay_days": d_task.delay_days
            })
            
    # Calculate longest downstream path depth
    depth = 0
    cascade_chain = [target_task.name]
    if task_id in G and descendants:
        paths = []
        for d_id in descendants:
            for p in nx.all_simple_paths(G, source=task_id, target=d_id):
                paths.append(p)
        if paths:
            longest_path = max(paths, key=len)
            depth = len(longest_path) - 1
            cascade_chain = [task_map[pid].name for pid in longest_path if pid in task_map]
            
    # Calculate downstream impact days
    task_delay = getattr(target_task, "delay_days", 0)
    impact_multiplier = 1.0 + (depth * 0.15)
    total_downstream_impact_days = int(round(task_delay * impact_multiplier))
    
    return {
        "task_id": target_task.id,
        "task_name": target_task.name,
        "current_delay_days": task_delay,
        "direct_dependents": direct_dependents,
        "downstream_tasks": downstream_tasks,
        "dependency_depth": depth,
        "is_on_critical_path": depth >= 3,
        "total_downstream_impact_days": total_downstream_impact_days,
        "cascade_chain": cascade_chain
    }

def get_graph_export(tasks: List[Any], dependencies: List[Any], critical_path_ids: List[int] = None) -> Dict[str, Any]:
    """
    Returns graph representation formatted for front-end visualizers.
    """
    crit_set = set(critical_path_ids or [])
    nodes = []
    edges = []
    
    for t in tasks:
        nodes.append({
            "id": t.id,
            "name": t.name,
            "team": t.team,
            "status": t.status,
            "progress": t.progress_percentage,
            "delay_days": t.delay_days,
            "priority": t.priority,
            "is_critical": t.id in crit_set
        })
        
    for d in dependencies:
        edges.append({
            "id": d.id,
            "source": d.source_task_id,
            "target": d.dependent_task_id,
            "type": d.dependency_type,
            "strength": d.dependency_strength,
            "is_critical": (d.source_task_id in crit_set and d.dependent_task_id in crit_set)
        })
        
    return {"nodes": nodes, "edges": edges}
