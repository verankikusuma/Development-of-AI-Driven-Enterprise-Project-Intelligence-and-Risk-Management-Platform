import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from app.ml.feature_extractor import FEATURE_NAMES
from app.core.config import settings

_model = None
_metadata = None

def get_model():
    global _model, _metadata
    if _model is None:
        if os.path.exists(settings.MODEL_PATH):
            try:
                _model = joblib.load(settings.MODEL_PATH)
            except Exception as e:
                print(f"Error loading model from {settings.MODEL_PATH}: {e}")
                _model = None
        
        if os.path.exists(settings.METADATA_PATH):
            try:
                with open(settings.METADATA_PATH, "r") as f:
                    _metadata = json.load(f)
            except Exception as e:
                print(f"Error reading metadata: {e}")
                _metadata = None
                
    return _model, _metadata

def predict_project_risk(features_dict: Dict[str, float]) -> Tuple[float, str, List[Dict[str, Any]]]:
    """
    Computes continuous risk probability [0.0 - 1.0] and risk classification level.
    """
    model, metadata = get_model()
    
    # Ensure ordered vector
    feature_row = [features_dict.get(k, 0.0) for k in FEATURE_NAMES]
    df_in = pd.DataFrame([feature_row], columns=FEATURE_NAMES)
    
    if model is not None:
        try:
            # Predict continuous probability using calibrated classifier probabilities
            prob = float(model.predict_proba(df_in)[0][1])
        except Exception:
            prob = _fallback_probabilistic_formula(features_dict)
    else:
        prob = _fallback_probabilistic_formula(features_dict)
        
    prob = max(0.01, min(0.99, round(prob, 4)))
    
    # Categorize Risk Level
    if prob < 0.30:
        level = "LOW"
    elif prob < 0.55:
        level = "MEDIUM"
    elif prob < 0.75:
        level = "HIGH"
    else:
        level = "CRITICAL"
        
    # Generate feature contributions
    factors = explain_risk_factors(features_dict, prob, metadata)
    
    return prob, level, factors

def _fallback_probabilistic_formula(f: Dict[str, float]) -> float:
    """
    Calibrated logistic regression baseline if model binary is not pre-compiled.
    """
    latent = (
        0.24 * (f.get("dependency_delay", 0) / 20.0)
        + 0.20 * (f.get("delay_days", 0) / 15.0)
        + 0.18 * (1.0 - (f.get("testing_progress", 50.0) / 100.0))
        + 0.16 * (1.0 - f.get("resource_availability", 1.0))
        + 0.12 * (f.get("testing_failure_rate", 0) * 2.0)
        + 0.10 * (f.get("bugs_per_task", 0) / 5.0)
        + 0.08 * (f.get("critical_dependency_count", 2) / 8.0)
        + 0.06 * (1.0 - (f.get("security_audit_progress", 50.0) / 100.0))
        - 0.10 * (f.get("team_productivity", 1.0) - 1.0)
    )
    return float(1.0 / (1.0 + np.exp(-3.2 * (latent - 0.4))))

def explain_risk_factors(
    features_dict: Dict[str, float],
    risk_prob: float,
    metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Calculates normalized factor contributions.
    """
    importance_map = (
        metadata.get("feature_importances", {}) if metadata else {
            "dependency_delay": 0.22,
            "delay_days": 0.18,
            "testing_progress": 0.16,
            "resource_availability": 0.14,
            "testing_failure_rate": 0.12,
            "bugs_per_task": 0.10,
            "critical_dependency_count": 0.08,
            "security_audit_progress": 0.08,
            "schedule_variance": 0.06,
            "resource_pressure": 0.06
        }
    )
    
    factor_definitions = [
        {
            "key": "dependency_delay",
            "name": "Dependency Delay Cascade",
            "unit": "days",
            "val": features_dict.get("dependency_delay", 0),
            "desc": "Upstream delay propagating through finish-to-start task chains"
        },
        {
            "key": "delay_days",
            "name": "Direct Task Delays",
            "unit": "days",
            "val": features_dict.get("delay_days", 0),
            "desc": "Accumulated schedule slips across active project work packages"
        },
        {
            "key": "testing_progress",
            "name": "Testing & Safety Progress Lag",
            "unit": "%",
            "val": features_dict.get("testing_progress", 0),
            "desc": "Autonomous driving and safety testing completion status vs baseline"
        },
        {
            "key": "resource_availability",
            "name": "Resource Availability Shortage",
            "unit": "%",
            "val": round((1.0 - features_dict.get("resource_availability", 1.0)) * 100, 1),
            "desc": "Deficit in engineering personnel and specialized hardware kits"
        },
        {
            "key": "testing_failure_rate",
            "name": "Testing Failure Rate",
            "unit": "%",
            "val": round(features_dict.get("testing_failure_rate", 0) * 100, 1),
            "desc": "Ratio of failed test runs in autonomous integration suites"
        },
        {
            "key": "bugs_per_task",
            "name": "Bug Density",
            "unit": "bugs/task",
            "val": round(features_dict.get("bugs_per_task", 0), 1),
            "desc": "Unresolved critical and high severity defects per active task"
        },
        {
            "key": "security_audit_progress",
            "name": "Cybersecurity Audit Deficit",
            "unit": "%",
            "val": round(100.0 - features_dict.get("security_audit_progress", 0), 1),
            "desc": "Remaining vulnerability mitigation and safety-integrity audits"
        },
        {
            "key": "critical_dependency_count",
            "name": "Critical Path Density",
            "unit": "links",
            "val": features_dict.get("critical_dependency_count", 0),
            "desc": "High-strength dependency links with zero schedule slack"
        }
    ]
    
    factors = []
    total_score = 0.0
    
    for item in factor_definitions:
        k = item["key"]
        weight = importance_map.get(k, 0.08)
        # Score increases when anomaly or risk driver is present
        raw_val = item["val"]
        score = weight * min(1.0, (raw_val / (25.0 if item["unit"] == "days" else 100.0 if item["unit"] == "%" else 5.0)))
        total_score += score
        
        level = "LOW"
        if score > 0.14 or (k == "dependency_delay" and raw_val > 5):
            level = "CRITICAL"
        elif score > 0.09 or (k in ["testing_progress", "resource_availability"] and raw_val > 20):
            level = "HIGH"
        elif score > 0.04:
            level = "MEDIUM"
            
        factors.append({
            "name": item["name"],
            "feature_key": k,
            "contribution_score": round(float(score), 4),
            "level": level,
            "value": float(raw_val),
            "unit": item["unit"],
            "description": item["desc"]
        })
        
    # Sort descending by contribution score
    factors.sort(key=lambda x: x["contribution_score"], reverse=True)
    return factors
