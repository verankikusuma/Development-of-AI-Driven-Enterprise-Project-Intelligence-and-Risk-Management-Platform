import os
import json
import joblib
import pandas as pd
import numpy as np

# Workaround for XGBoost on NumPy 2.0 (np.NaN was removed)
if not hasattr(np, "NaN"):
    np.NaN = np.nan

import xgboost as xgb
import streamlit as st

IT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "it_models", "xgb_project_risk_model.json")
NON_IT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "non_it_models", "risk_model.joblib")

_it_feature_names = []
_it_feature_types = []

@st.cache_resource(show_spinner=False)
def load_it_model():
    global _it_feature_names, _it_feature_types
    if os.path.exists(IT_MODEL_PATH):
        with open(IT_MODEL_PATH, "r") as f:
            d = json.load(f)
            _it_feature_names = d['learner']['feature_names']
            _it_feature_types = d['learner']['feature_types']
        model = xgb.Booster()
        model.load_model(IT_MODEL_PATH)
        return model, _it_feature_names, _it_feature_types
    return None, [], []

@st.cache_resource(show_spinner=False)
def load_non_it_model():
    if os.path.exists(NON_IT_MODEL_PATH):
        return joblib.load(NON_IT_MODEL_PATH)
    return None

def get_risk_level(score):
    if score < 30: return "Low"
    if score < 55: return "Medium"
    if score < 75: return "High"
    return "Critical"

def predict_it_risk(features_dict, skip_api: bool = False):
    """
    Predicts risk for IT projects. Uses backend FastAPI API endpoint when active,
    with fallback to local XGBoost engine.
    """
    # 1. Try FastAPI Backend API first
    if not skip_api:
        try:
            from utils.api_client import backend_health, api_predict_it_risk
            api_base = "http://127.0.0.1:8000"
            try:
                api_base = st.session_state.get("api_base", api_base)
            except Exception:
                pass
            if backend_health(api_base):
                api_res = api_predict_it_risk(features_dict, base_url=api_base)
                if api_res and "risk_score" in api_res:
                    return _enrich_prediction(api_res, features_dict)
        except Exception:
            pass

    # 2. Local XGBoost Engine Fallback
    model, f_names, f_types = load_it_model()
    if not model or not f_names:
        return _enrich_prediction({"risk_score": 50.0, "risk_level": "Medium"}, features_dict)

    df = pd.DataFrame([features_dict])
    cat_cols = [c for c, t in zip(f_names, f_types) if t == "c"]
    
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    missing_cols = [c for c in f_names if c not in df.columns]
    for col in missing_cols:
        if col in cat_cols:
            df[col] = pd.Series(["Unknown"], dtype="category")
        else:
            df[col] = 0.0

    df = df[f_names]
    dmat = xgb.DMatrix(df, enable_categorical=True)
    pred = model.predict(dmat)[0]
    score = float(max(0, min(100, pred)))
    payload = {
        "risk_score": round(score, 1),
        "risk_level": get_risk_level(score)
    }
    return _enrich_prediction(payload, features_dict, model=model, dmat=dmat, feature_names=f_names)

def predict_non_it_risk(features_dict, skip_api: bool = False):
    """
    Predicts risk for Non-IT projects using ML model pipeline with fallback to dynamic risk telemetry.
    """
    # 1. Try FastAPI Backend API first
    if not skip_api:
        try:
            from utils.api_client import backend_health, api_predict_non_it_risk
            api_base = "http://127.0.0.1:8000"
            try:
                api_base = st.session_state.get("api_base", api_base)
            except Exception:
                pass
            if backend_health(api_base):
                api_res = api_predict_non_it_risk(features_dict, base_url=api_base)
                if api_res and "risk_score" in api_res and api_res["risk_score"] > 0:
                    return _enrich_prediction(api_res, features_dict)
        except Exception:
            pass

    # 2. Local Model Engine Fallback
    model = load_non_it_model()
    score = 0.0

    if features_dict:
        # Calculate dynamic domain risk score from extracted document parameters
        tech = float(features_dict.get("tech_complexity_score", 40.0))
        ext = float(features_dict.get("external_dependency_score", 35.0))
        reg = float(features_dict.get("regulatory_compliance_load", 20.0))
        sched = float(features_dict.get("schedule_overrun_pct", 0.0))
        res_avail = float(features_dict.get("resource_availability_pct", 85.0))
        scope_clar = float(features_dict.get("scope_clarity_score", 75.0))
        vendor_cnt = float(features_dict.get("vendor_dependency_count", 0.0))
        turnover = float(features_dict.get("team_turnover_pct", 5.0))

        # Try evaluating loaded ML model binary first if valid features match model schema
        if model:
            try:
                df = pd.DataFrame([features_dict])
                if hasattr(model, "feature_names_in_"):
                    for col in model.feature_names_in_:
                        if col not in df.columns:
                            df[col] = 0.0
                    df = df[model.feature_names_in_]
                proba = model.predict_proba(df)[0][1]
                score = float(proba * 100.0)
            except Exception:
                score = 0.0

        # Fallback to dynamic domain formula if model output is zero or invalid
        if score <= 0.0:
            calc_score = (
                0.24 * tech +
                0.22 * ext +
                0.18 * reg +
                0.18 * (sched * 2.2) +
                0.15 * (100.0 - res_avail) +
                0.12 * (100.0 - scope_clar) +
                0.10 * (vendor_cnt * 10.0) +
                0.08 * (turnover * 1.5)
            )
            score = float(max(15.0, min(95.0, calc_score)))

    if score <= 0.0:
        score = 45.0

    return _enrich_prediction({
        "risk_score": round(score, 1),
        "risk_level": get_risk_level(score)
    }, features_dict)


def _band_probabilities(score: float) -> dict:
    """Soft class distribution around the existing 0-100 score. Does not change the predicted class."""
    centers = {"Low": 15.0, "Medium": 42.0, "High": 65.0, "Critical": 87.0}
    weights = {}
    for name, center in centers.items():
        dist = abs(score - center)
        weights[name] = float(np.exp(-((dist / 18.0) ** 2)))
    total = sum(weights.values()) or 1.0
    return {k: round(v / total, 4) for k, v in weights.items()}


def _confidence_from_score(score: float, probs: dict, level: str) -> float:
    p = float(probs.get(level, 0.0))
    # Distance from nearest threshold (30, 55, 75)
    thresholds = [30.0, 55.0, 75.0]
    dist = min(abs(score - t) for t in thresholds)
    margin = min(1.0, dist / 12.0)
    return round(max(0.35, min(0.95, 0.45 * p + 0.50 * margin + 0.05)), 3)


def _enrich_prediction(payload, features_dict, model=None, dmat=None, feature_names=None):
    """Add class, confidence, probabilities, and contributing factors without retraining."""
    if not isinstance(payload, dict):
        return payload
    score = float(payload.get("risk_score", 50.0) or 50.0)
    level = payload.get("risk_level") or get_risk_level(score)
    probs = payload.get("probabilities") or _band_probabilities(score)
    out = dict(payload)
    out["risk_level"] = level
    out["predicted_class"] = level
    out["probabilities"] = probs
    out["confidence"] = payload.get("confidence") or _confidence_from_score(score, probs, level)
    if not out.get("contributing_factors"):
        out["contributing_factors"] = _contributing_factors(features_dict or {}, model, dmat, feature_names)
    return out


def _contributing_factors(features_dict, model=None, dmat=None, feature_names=None):
    factors = []
    if model is not None and dmat is not None and feature_names:
        try:
            contrib = model.predict(dmat, pred_contrib=True)[0]
            pairs = list(zip(feature_names, contrib[:-1] if len(contrib) == len(feature_names) + 1 else contrib))
            pairs.sort(key=lambda x: abs(float(x[1])), reverse=True)
            for name, val in pairs[:8]:
                factors.append({
                    "feature": name,
                    "name": name,
                    "contribution": round(float(val), 4),
                    "impact": "increases risk" if float(val) > 0 else "decreases risk",
                })
            if factors:
                return factors
        except Exception:
            pass
    ranked = []
    for key, val in (features_dict or {}).items():
        try:
            ranked.append((key, abs(float(val))))
        except (TypeError, ValueError):
            continue
    ranked.sort(key=lambda x: x[1], reverse=True)
    for key, _ in ranked[:8]:
        factors.append({
            "feature": key,
            "name": key,
            "contribution": features_dict.get(key),
            "impact": "input attribute",
        })
    return factors

