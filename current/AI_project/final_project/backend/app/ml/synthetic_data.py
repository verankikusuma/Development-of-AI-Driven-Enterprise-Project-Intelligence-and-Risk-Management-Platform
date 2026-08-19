import numpy as np
import pandas as pd
from app.ml.feature_extractor import FEATURE_NAMES

def generate_synthetic_dataset(num_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic, non-trivial synthetic historical project records with realistic noise.
    
    Synthetic data is utilized for prototype validation; real historical project data
    is required for production enterprise risk forecasting.
    """
    np.random.seed(random_seed)
    
    # 1. Base progress distribution (0 to 100%)
    progress_percentage = np.random.uniform(10.0, 95.0, num_samples)
    
    # 2. Correlated features
    # As progress increases, pending ratio decreases with realistic variance
    pending_task_ratio = np.clip(1.0 - (progress_percentage / 100.0) + np.random.normal(0, 0.08, num_samples), 0.05, 1.0)
    
    # Delay days (exponential/gamma with progress pressure)
    delay_days = np.clip(np.random.gamma(shape=2.0, scale=3.5, size=num_samples) * (1.2 - progress_percentage / 120.0), 0, 45)
    
    # Budget utilization
    budget_utilization = np.clip((progress_percentage / 100.0) * np.random.uniform(0.9, 1.4, num_samples), 0.1, 1.6)
    
    # Resource availability (0.4 to 1.0)
    resource_availability = np.clip(np.random.beta(a=6, b=2, size=num_samples), 0.35, 1.0)
    
    # Bugs reported per task
    bugs_per_task = np.clip(np.random.poisson(lam=2.5, size=num_samples) + np.random.exponential(scale=1.0, size=num_samples), 0.0, 15.0)
    
    # Testing progress & failure rate
    testing_progress = np.clip(progress_percentage * np.random.uniform(0.7, 1.1, num_samples), 0.0, 100.0)
    testing_failure_rate = np.clip(np.random.beta(a=2, b=8, size=num_samples) + (delay_days / 150.0), 0.0, 0.9)
    
    # Requirement changes & Team productivity
    requirement_change_rate = np.clip(np.random.exponential(scale=0.8, size=num_samples), 0.0, 6.0)
    team_productivity = np.clip(np.random.normal(loc=1.0, scale=0.2, size=num_samples), 0.5, 1.8)
    
    # Dependency delay & critical dependencies count
    critical_dependency_count = np.random.randint(1, 12, num_samples)
    dependency_delay = np.clip(delay_days * np.random.uniform(0.6, 1.8, num_samples) + (critical_dependency_count * 0.8), 0, 60)
    
    # Security audit progress & External risk
    security_audit_progress = np.clip(progress_percentage * np.random.uniform(0.6, 1.05, num_samples), 0.0, 100.0)
    external_risk_score = np.clip(np.random.beta(a=2, b=5, size=num_samples), 0.05, 0.95)
    
    # Schedule variance
    schedule_variance = delay_days - (progress_percentage * 0.1) + np.random.normal(0, 1.5, num_samples)
    
    # Derived composite features
    resource_pressure = np.clip((1.0 - resource_availability) * 1.5 + (pending_task_ratio * 0.5), 0.0, 1.0)
    dependency_risk_score = np.clip((dependency_delay * 0.04) + (critical_dependency_count * 0.07), 0.0, 1.0)
    
    df = pd.DataFrame({
        "progress_percentage": progress_percentage,
        "pending_task_ratio": pending_task_ratio,
        "delay_days": delay_days,
        "budget_utilization": budget_utilization,
        "resource_availability": resource_availability,
        "bugs_per_task": bugs_per_task,
        "testing_progress": testing_progress,
        "testing_failure_rate": testing_failure_rate,
        "requirement_change_rate": requirement_change_rate,
        "team_productivity": team_productivity,
        "dependency_delay": dependency_delay,
        "critical_dependency_count": critical_dependency_count,
        "security_audit_progress": security_audit_progress,
        "external_risk_score": external_risk_score,
        "schedule_variance": schedule_variance,
        "resource_pressure": resource_pressure,
        "dependency_risk_score": dependency_risk_score
    })
    
    # Non-linear ground truth risk formula with realistic interactions and noise
    # Heavy weighting on dependency delays, testing lag, resource shortages, and bug spikes
    latent_risk_score = (
        0.22 * (dependency_delay / 25.0)
        + 0.18 * (delay_days / 20.0)
        + 0.16 * (1.0 - (testing_progress / 100.0))
        + 0.14 * (1.0 - resource_availability)
        + 0.12 * (testing_failure_rate * 2.0)
        + 0.10 * (bugs_per_task / 6.0)
        + 0.08 * (1.0 - (security_audit_progress / 100.0))
        + 0.08 * (budget_utilization - 1.0)
        + 0.06 * external_risk_score
        - 0.12 * (team_productivity - 1.0)
        + np.random.normal(0, 0.12, num_samples) # Stochastic variance
    )
    
    # Sigmoid to convert to true continuous probability [0.0, 1.0]
    true_probability = 1.0 / (1.0 + np.exp(-3.2 * (latent_risk_score - 0.45)))
    df["true_risk_probability"] = np.clip(true_probability, 0.01, 0.99)
    
    # Binary classification target (1 = High/Critical Risk Project requiring intervention)
    df["is_high_risk"] = (df["true_risk_probability"] >= 0.55).astype(int)
    
    # Categorical classification label
    conditions = [
        df["true_risk_probability"] < 0.30,
        (df["true_risk_probability"] >= 0.30) & (df["true_risk_probability"] < 0.55),
        (df["true_risk_probability"] >= 0.55) & (df["true_risk_probability"] < 0.75),
        df["true_risk_probability"] >= 0.75
    ]
    choices = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    df["risk_level"] = np.select(conditions, choices, default="MEDIUM")
    
    return df
