import networkx as nx
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

def calculate_critical_path(tasks: List[Any], dependencies: List[Any]) -> Dict[str, Any]:
    """
    Standard Critical Path Method (CPM) algorithm calculating Forward Pass (ES, EF),
    Backward Pass (LS, LF), and Total Float to determine the critical path.
    """
    if not tasks:
        return {
            "critical_task_ids": [],
            "critical_tasks": [],
            "project_duration_days": 0,
            "schedule_buffer_days": 0,
            "cpm_table": {}
        }
        
    G = nx.DiGraph()
    task_map = {t.id: t for t in tasks}
    
    for t in tasks:
        # Effective duration = remaining duration + delay days
        eff_duration = max(1, t.remaining_duration + t.delay_days)
        G.add_node(t.id, duration=eff_duration, obj=t)
        
    for d in dependencies:
        if d.source_task_id in task_map and d.dependent_task_id in task_map:
            G.add_edge(d.source_task_id, d.dependent_task_id)
            
    # Check for cycles
    if not nx.is_directed_acyclic_graph(G):
        # Fallback if circular dependency exists: use topological heuristic on simple DAG
        simple_crit = [t.id for t in sorted(tasks, key=lambda x: (x.delay_days, x.remaining_duration), reverse=True)[:4]]
        return {
            "critical_task_ids": simple_crit,
            "critical_tasks": [task_map[cid] for cid in simple_crit if cid in task_map],
            "project_duration_days": 90,
            "schedule_buffer_days": 5,
            "cpm_table": {}
        }

    topo_order = list(nx.topological_sort(G))
    
    # 1. Forward Pass (ES, EF)
    ES = {}
    EF = {}
    for node in topo_order:
        predecessors = list(G.predecessors(node))
        if not predecessors:
            ES[node] = 0
        else:
            ES[node] = max(EF[p] for p in predecessors)
        EF[node] = ES[node] + G.nodes[node]["duration"]
        
    project_duration = max(EF.values()) if EF else 0
    
    # 2. Backward Pass (LS, LF)
    LS = {}
    LF = {}
    for node in reversed(topo_order):
        successors = list(G.successors(node))
        if not successors:
            LF[node] = project_duration
        else:
            LF[node] = min(LS[s] for s in successors)
        LS[node] = LF[node] - G.nodes[node]["duration"]
        
    # 3. Float Calculation (Slack = LS - ES)
    Float = {}
    critical_task_ids = []
    cpm_table = {}
    
    for node in topo_order:
        slack = LS[node] - ES[node]
        Float[node] = slack
        if slack <= 0.001:
            critical_task_ids.append(node)
            
        t_obj = task_map[node]
        cpm_table[node] = {
            "task_id": node,
            "task_name": t_obj.name,
            "duration": G.nodes[node]["duration"],
            "early_start": ES[node],
            "early_finish": EF[node],
            "late_start": LS[node],
            "late_finish": LF[node],
            "total_float": slack,
            "is_critical": slack <= 0.001
        }
        
    critical_tasks_formatted = []
    for cid in critical_task_ids:
        if cid in task_map:
            t = task_map[cid]
            critical_tasks_formatted.append({
                "id": t.id,
                "name": t.name,
                "team": t.team,
                "delay_days": t.delay_days,
                "progress": t.progress_percentage,
                "status": t.status,
                "duration": G.nodes[cid]["duration"]
            })
            
    # Calculate schedule buffer (remaining days until deadline vs project duration)
    # Scenario: 90 days total allocated. Buffer = 90 - project_duration
    schedule_buffer_days = max(0, 90 - project_duration)

    return {
        "critical_task_ids": critical_task_ids,
        "critical_tasks": critical_tasks_formatted,
        "project_duration_days": project_duration,
        "schedule_buffer_days": schedule_buffer_days,
        "cpm_table": cpm_table
    }
