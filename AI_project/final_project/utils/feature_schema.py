# Feature schema for IT XGBoost Model

IT_FEATURE_CATEGORIES = {
    "project_type": ["Software Development", "Infrastructure", "Cloud Migration", "Data Analytics", "ERP Implementation", "Cybersecurity", "Unknown"],
    "industry_sector": ["Technology", "Finance", "Healthcare", "Manufacturing", "Retail", "Energy", "Unknown"],
    "methodology": ["Agile", "Waterfall", "Scrum", "Kanban", "Hybrid", "Unknown"],
    "region": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa", "Unknown"],
    "contract_type": ["Fixed Price", "Time & Material", "Retainer", "Unknown"],
    "priority": ["Low", "Medium", "High", "Critical", "Unknown"]
}

IT_FEATURE_NUMERIC = [
    "planned_duration_days", "actual_duration_days", "team_size", "team_avg_experience_years", 
    "team_turnover_pct", "stakeholder_count", "requirement_changes_count", "budget_usd", 
    "actual_cost_usd", "cost_overrun_pct", "schedule_overrun_pct", "resource_availability_pct", 
    "vendor_dependency_count", "communication_score", "sponsor_engagement_score", 
    "previous_project_success_rate_pct", "tech_complexity_score", "regulatory_compliance_load", 
    "scope_clarity_score", "external_dependency_score", "safety_incidents", "defect_count", 
    "milestones_missed"
]

NON_IT_FEATURE_NUMERIC = [
    "progress_percentage", "pending_task_ratio", "delay_days", "budget_utilization",
    "resource_availability", "bugs_per_task", "testing_progress", "testing_failure_rate",
    "requirement_change_rate", "team_productivity", "dependency_delay", "critical_dependency_count",
    "security_audit_progress", "external_risk_score", "schedule_variance", "resource_pressure",
    "dependency_risk_score"
]
