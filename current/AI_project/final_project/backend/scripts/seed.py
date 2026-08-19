from datetime import datetime, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.project import Project
from app.models.task import Task
from app.models.dependency import Dependency
from app.models.metrics import ProjectMetrics
from app.models.risk import RiskPrediction
from app.ml.feature_extractor import extract_features_from_project_state
from app.ml.predict import predict_project_risk

def seed_driverless_metro_project():
    print("Seeding India Driverless Metro Launch project...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data for clean idempotent seed
    db.query(RiskPrediction).delete()
    db.query(ProjectMetrics).delete()
    db.query(Dependency).delete()
    db.query(Task).delete()
    db.query(Project).delete()
    db.commit()

    now = datetime.utcnow()
    # August 15 deadline (90 days from project commencement)
    deadline = now + timedelta(days=90)
    start_date = now - timedelta(days=60)

    # 1. Project Record
    metro_project = Project(
        name="India Driverless Metro Launch",
        description=(
            "National high-priority launch of the fully autonomous, AI-driven driverless metro rail network. "
            "Integrates grade-of-automation GoA4 autonomous train control, optical sensor arrays, "
            "redundant fail-safe braking mechanisms, real-time telemetry, and government safety certification."
        ),
        start_date=start_date,
        deadline=deadline,
        budget=85000000.0, # $85M
        current_budget_used=62400000.0, # $62.4M
        status="AT_RISK"
    )
    db.add(metro_project)
    db.commit()
    db.refresh(metro_project)
    p_id = metro_project.id

    # 2. 12 Tasks with realistic status, team assignments, delays and progress
    task_data = [
        {
            "name": "Railway Track Construction",
            "team": "Track Infrastructure",
            "progress_percentage": 92.0,
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "estimated_duration": 45,
            "remaining_duration": 4,
            "resource_count": 28,
            "resource_availability": 0.95,
            "pending_tasks": 1,
            "bugs_reported": 0,
            "requirement_changes": 1,
            "delay_days": 0,
            "description": "Laying of ballastless high-speed tracks, turnouts, and third-rail electrification."
        },
        {
            "name": "Station Infrastructure",
            "team": "Civil Engineering & Stations",
            "progress_percentage": 88.0,
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
            "estimated_duration": 40,
            "remaining_duration": 5,
            "resource_count": 20,
            "resource_availability": 0.90,
            "pending_tasks": 2,
            "bugs_reported": 1,
            "requirement_changes": 2,
            "delay_days": 0,
            "description": "Platform screen doors (PSD), concourse ticketing, and automated passenger safety barriers."
        },
        {
            "name": "Sensor & Camera Installation",
            "team": "Sensor Systems & Hardware",
            "progress_percentage": 64.0,
            "status": "DELAYED",
            "priority": "CRITICAL",
            "estimated_duration": 30,
            "remaining_duration": 12,
            "resource_count": 12,
            "resource_availability": 0.70,
            "pending_tasks": 4,
            "bugs_reported": 5,
            "requirement_changes": 3,
            "delay_days": 4,
            "description": "Mounting of LiDAR arrays, thermal obstacle cameras, radar sensors, and track alignment lasers."
        },
        {
            "name": "AI Autonomous Driving Software",
            "team": "Autonomous Core AI",
            "progress_percentage": 72.0,
            "status": "IN_PROGRESS",
            "priority": "CRITICAL",
            "estimated_duration": 50,
            "remaining_duration": 14,
            "resource_count": 18,
            "resource_availability": 0.85,
            "pending_tasks": 3,
            "bugs_reported": 6,
            "requirement_changes": 4,
            "delay_days": 2,
            "description": "GoA4 deep neural network control stack, dynamic speed profiling, and precision platform docking."
        },
        {
            "name": "Emergency Braking System",
            "team": "Safety Mechanics",
            "progress_percentage": 78.0,
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "estimated_duration": 35,
            "remaining_duration": 8,
            "resource_count": 10,
            "resource_availability": 0.90,
            "pending_tasks": 2,
            "bugs_reported": 2,
            "requirement_changes": 1,
            "delay_days": 1,
            "description": "Triple-redundant electro-pneumatic friction brakes and automatic fail-safe trip stops."
        },
        {
            "name": "Communication Infrastructure",
            "team": "Network & Telemetry",
            "progress_percentage": 80.0,
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
            "estimated_duration": 30,
            "remaining_duration": 6,
            "resource_count": 8,
            "resource_availability": 0.92,
            "pending_tasks": 2,
            "bugs_reported": 1,
            "requirement_changes": 0,
            "delay_days": 0,
            "description": "Ultra-reliable low-latency 5G-LTE-R train-to-ground mission critical communications (CBTC)."
        },
        {
            "name": "Cybersecurity Audit",
            "team": "InfoSec & Cyber Defense",
            "progress_percentage": 60.0,
            "status": "DELAYED",
            "priority": "HIGH",
            "estimated_duration": 25,
            "remaining_duration": 10,
            "resource_count": 7,
            "resource_availability": 0.75,
            "pending_tasks": 3,
            "bugs_reported": 4,
            "requirement_changes": 2,
            "delay_days": 3,
            "description": "IEC 62443 industrial cyber posture audit, train bus cryptographic integrity, and penetration tests."
        },
        {
            "name": "Safety Testing",
            "team": "Quality & Safety Verification",
            "progress_percentage": 52.0,
            "status": "BLOCKED",
            "priority": "CRITICAL",
            "estimated_duration": 35,
            "remaining_duration": 18,
            "resource_count": 14,
            "resource_availability": 0.65,
            "pending_tasks": 6,
            "bugs_reported": 8,
            "requirement_changes": 5,
            "delay_days": 5,
            "description": "Comprehensive obstacle collision avoidance tests, emergency stop distance verification, and degraded mode runs."
        },
        {
            "name": "Control Room Setup",
            "team": "Operations Control Center (OCC)",
            "progress_percentage": 85.0,
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
            "estimated_duration": 25,
            "remaining_duration": 4,
            "resource_count": 12,
            "resource_availability": 0.95,
            "pending_tasks": 1,
            "bugs_reported": 1,
            "requirement_changes": 0,
            "delay_days": 0,
            "description": "Centralized video wall, dispatch telematics consoles, and automated power scada workstations."
        },
        {
            "name": "Government Safety Certification",
            "team": "Regulatory Affairs & CMRS",
            "progress_percentage": 35.0,
            "status": "DELAYED",
            "priority": "CRITICAL",
            "estimated_duration": 30,
            "remaining_duration": 20,
            "resource_count": 6,
            "resource_availability": 0.70,
            "pending_tasks": 5,
            "bugs_reported": 3,
            "requirement_changes": 3,
            "delay_days": 4,
            "description": "Commissioner of Metro Railway Safety (CMRS) statutory compliance, SIL-4 safety case dossier sign-off."
        },
        {
            "name": "Final System Integration",
            "team": "System Integration",
            "progress_percentage": 45.0,
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "estimated_duration": 28,
            "remaining_duration": 15,
            "resource_count": 15,
            "resource_availability": 0.80,
            "pending_tasks": 4,
            "bugs_reported": 5,
            "requirement_changes": 2,
            "delay_days": 3,
            "description": "Full end-to-end integration between rolling stock, signaling, track power, and central dispatch."
        },
        {
            "name": "Launch Preparation",
            "team": "PMO & Metro Operations",
            "progress_percentage": 30.0,
            "status": "NOT_STARTED",
            "priority": "CRITICAL",
            "estimated_duration": 20,
            "remaining_duration": 14,
            "resource_count": 22,
            "resource_availability": 0.90,
            "pending_tasks": 7,
            "bugs_reported": 0,
            "requirement_changes": 1,
            "delay_days": 0,
            "description": "Trial passenger simulation runs, emergency drill protocol certification, and VIP flag-off inauguration readiness."
        }
    ]

    task_objects = {}
    for i, tdata in enumerate(task_data):
        planned_end = now + timedelta(days=tdata["remaining_duration"] + 5)
        task = Task(
            project_id=p_id,
            name=tdata["name"],
            team=tdata["team"],
            start_date=start_date + timedelta(days=i * 4),
            planned_end_date=planned_end,
            progress_percentage=tdata["progress_percentage"],
            status=tdata["status"],
            priority=tdata["priority"],
            estimated_duration=tdata["estimated_duration"],
            remaining_duration=tdata["remaining_duration"],
            resource_count=tdata["resource_count"],
            resource_availability=tdata["resource_availability"],
            pending_tasks=tdata["pending_tasks"],
            bugs_reported=tdata["bugs_reported"],
            requirement_changes=tdata["requirement_changes"],
            delay_days=tdata["delay_days"],
            description=tdata["description"]
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        task_objects[tdata["name"]] = task

    # 3. Dependencies
    dep_links = [
        ("Railway Track Construction", "Final System Integration", 0.85),
        ("Sensor & Camera Installation", "AI Autonomous Driving Software", 0.95),
        ("AI Autonomous Driving Software", "Safety Testing", 1.0),
        ("Emergency Braking System", "Safety Testing", 0.90),
        ("Communication Infrastructure", "Final System Integration", 0.80),
        ("Cybersecurity Audit", "Government Safety Certification", 0.90),
        ("Safety Testing", "Government Safety Certification", 1.0),
        ("Government Safety Certification", "Launch Preparation", 1.0),
        ("Final System Integration", "Launch Preparation", 0.95),
        ("Control Room Setup", "Launch Preparation", 0.75),
        ("Station Infrastructure", "Launch Preparation", 0.70),
    ]

    for src_name, tgt_name, strength in dep_links:
        if src_name in task_objects and tgt_name in task_objects:
            dep = Dependency(
                project_id=p_id,
                source_task_id=task_objects[src_name].id,
                dependent_task_id=task_objects[tgt_name].id,
                dependency_type="FINISH_TO_START",
                dependency_strength=strength
            )
            db.add(dep)
    db.commit()

    # 4. Realistic Historical Project Metrics
    historical_metrics = [
        {"day_offset": 60, "prog": 15.0, "del_days": 0, "bugs": 4, "test_prog": 10.0, "risk_prob": 0.24, "level": "LOW"},
        {"day_offset": 45, "prog": 32.0, "del_days": 1, "bugs": 9, "test_prog": 22.0, "risk_prob": 0.31, "level": "MEDIUM"},
        {"day_offset": 30, "prog": 48.0, "del_days": 3, "bugs": 15, "test_prog": 34.0, "risk_prob": 0.44, "level": "MEDIUM"},
        {"day_offset": 15, "prog": 58.0, "del_days": 7, "bugs": 22, "test_prog": 44.0, "risk_prob": 0.61, "level": "HIGH"},
        {"day_offset": 0,  "prog": 66.5, "del_days": 11, "bugs": 31, "test_prog": 52.0, "risk_prob": 0.78, "level": "CRITICAL"},
    ]

    for h in historical_metrics:
        ts = now - timedelta(days=h["day_offset"])
        met = ProjectMetrics(
            project_id=p_id,
            timestamp=ts,
            project_progress=h["prog"],
            pending_tasks=8,
            completed_tasks=4,
            delayed_tasks=4,
            budget_utilization=0.73,
            resource_availability=0.78,
            team_productivity=0.92,
            testing_progress=h["test_prog"],
            testing_failures=6,
            bugs=h["bugs"],
            requirement_changes=4,
            technical_issues=5,
            security_audit_progress=60.0,
            communication_failures=1,
            external_risk=0.35,
            dependency_delay=h["del_days"],
            schedule_variance=float(h["del_days"])
        )
        db.add(met)

        # Also store historical risk prediction record
        pred = RiskPrediction(
            project_id=p_id,
            prediction_timestamp=ts,
            model_version="1.0.0",
            risk_probability=h["risk_prob"],
            risk_level=h["level"],
            feature_snapshot={"progress": h["prog"], "delay_days": h["del_days"]},
            contributing_factors=[]
        )
        db.add(pred)

    db.commit()

    # 5. Extract latest feature snapshot & generate live risk prediction
    all_tasks = db.query(Task).filter(Task.project_id == p_id).all()
    all_deps = db.query(Dependency).filter(Dependency.project_id == p_id).all()
    latest_m = db.query(ProjectMetrics).filter(ProjectMetrics.project_id == p_id).order_by(ProjectMetrics.timestamp.desc()).first()

    feats = extract_features_from_project_state(all_tasks, all_deps, latest_m)
    prob, level, factors = predict_project_risk(feats)

    current_pred = RiskPrediction(
        project_id=p_id,
        prediction_timestamp=now,
        model_version="1.0.0",
        risk_probability=prob,
        risk_level=level,
        feature_snapshot=feats,
        contributing_factors=factors
    )
    db.add(current_pred)
    db.commit()

    print("Seed completed successfully!")
    print(f"Project '{metro_project.name}' (ID: {p_id}) initialized with 12 tasks, 11 dependencies, and active ML Risk Forecast ({level}, {prob*100:.1f}%).")
    db.close()

if __name__ == "__main__":
    seed_driverless_metro_project()
