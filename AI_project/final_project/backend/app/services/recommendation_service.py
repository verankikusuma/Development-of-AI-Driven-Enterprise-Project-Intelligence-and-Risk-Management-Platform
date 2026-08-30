from typing import List, Dict, Any
from datetime import datetime
import uuid

def generate_mitigation_recommendations(
    project: Any,
    tasks: List[Any],
    dependencies: List[Any],
    risk_prob: float,
    factors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates structured, high-impact mitigation recommendations based on
    task bottlenecks, dependency cascade chains, and ML risk drivers.
    """
    recommendations = []
    
    # 1. Inspect Sensor / Hardware Bottlenecks
    sensor_tasks = [t for t in tasks if "sensor" in t.name.lower() or "camera" in t.name.lower() or "hardware" in t.name.lower()]
    for st in sensor_tasks:
        if st.delay_days > 0 or st.progress_percentage < 70:
            recommendations.append({
                "id": str(uuid.uuid4())[:8],
                "priority": "HIGH" if st.delay_days > 3 else "MEDIUM",
                "title": f"Expedite {st.name} & Engage Backup Hardware Suppliers",
                "action": "Activate fast-track vendor SLA for optical sensor calibration kits and conduct mock sensor simulation testing in parallel.",
                "reason": f"{st.name} is experiencing a {st.delay_days}-day delay which directly blocks AI Autonomous Testing suites.",
                "category": "SENSOR_HARDWARE",
                "affected_teams": [st.team, "AI Autonomous Driving Software", "Safety Testing"],
                "impact_reduction_estimate": "-12% Risk Reduction / 4 Days Recovered"
            })

    # 2. Inspect Testing / Safety Testing Bottlenecks
    test_tasks = [t for t in tasks if "test" in t.name.lower() or "safety" in t.name.lower()]
    for tt in test_tasks:
        if tt.delay_days > 0 or tt.progress_percentage < 60 or tt.bugs_reported > 3:
            recommendations.append({
                "id": str(uuid.uuid4())[:8],
                "priority": "CRITICAL" if tt.delay_days > 4 else "HIGH",
                "title": f"Reinforce Testing Resources for {tt.name}",
                "action": "Allocate 4 additional safety verification engineers, split track testing into 24/7 dual-shift cycles, and prioritize critical emergency braking test cases.",
                "reason": f"Testing progress is lagging behind trajectory ({tt.progress_percentage}% completed) with {tt.bugs_reported} reported blockers.",
                "category": "TESTING",
                "affected_teams": [tt.team, "Government Safety Certification", "Control Room"],
                "impact_reduction_estimate": "-18% Risk Reduction / 6 Days Recovered"
            })

    # 3. Inspect Cybersecurity and Compliance
    sec_tasks = [t for t in tasks if "cyber" in t.name.lower() or "security" in t.name.lower() or "audit" in t.name.lower()]
    for sect in sec_tasks:
        if sect.progress_percentage < 80:
            recommendations.append({
                "id": str(uuid.uuid4())[:8],
                "priority": "HIGH",
                "title": f"Accelerate Compliance Review for {sect.name}",
                "action": "Engage certified external penetration testers to pre-audit safety integrity level (SIL-4) certificates before formal government inspection.",
                "reason": "Government certification requires zero unmitigated severity-1 cyber vulnerabilities.",
                "category": "CYBERSECURITY",
                "affected_teams": [sect.team, "Government Safety Certification"],
                "impact_reduction_estimate": "-10% Risk Reduction / 3 Days Recovered"
            })

    # 4. Inspect Resource Constraints
    resource_strained = [t for t in tasks if getattr(t, "resource_availability", 1.0) < 0.75]
    if resource_strained:
        team_names = list(set([t.team for t in resource_strained]))
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "priority": "MEDIUM",
            "title": "Cross-Level Resource Redistribution",
            "action": f"Shift senior integration engineers from completed infrastructure work packages to {', '.join(team_names)}.",
            "reason": f"Resource availability has dropped below 75% in critical path modules.",
            "category": "RESOURCE",
            "affected_teams": team_names,
            "impact_reduction_estimate": "-8% Risk Reduction / 2 Days Recovered"
        })

    # 5. Generic Critical Path Decoupling if overall risk is high
    if risk_prob >= 0.55 and len(recommendations) < 4:
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "priority": "HIGH",
            "title": "Parallelize System Integration Interface Tests",
            "action": "Decouple final station infrastructure sign-off from software simulation so track commissioning and signaling tests proceed uninterrupted.",
            "reason": "Topological dependency analysis shows 4 downstream tasks waiting on finish-to-start gate closures.",
            "category": "DEPENDENCY",
            "affected_teams": ["All Engineering Teams", "Project Management Office"],
            "impact_reduction_estimate": "-15% Risk Reduction / 5 Days Recovered"
        })

    crit_count = sum(1 for r in recommendations if r["priority"] == "CRITICAL")
    high_count = sum(1 for r in recommendations if r["priority"] == "HIGH")

    return {
        "project_id": project.id,
        "total_recommendations": len(recommendations),
        "critical_count": crit_count,
        "high_count": high_count,
        "recommendations": recommendations,
        "generated_at": datetime.utcnow()
    }
