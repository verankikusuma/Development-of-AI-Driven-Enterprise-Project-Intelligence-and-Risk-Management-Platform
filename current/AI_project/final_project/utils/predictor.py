import os
import json
import joblib
import pandas as pd
import numpy as np
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

def predict_it_risk(features_dict):
    """
    Predicts risk for IT projects. Uses backend FastAPI API endpoint when active,
    with fallback to local XGBoost engine.
    """
    # 1. Try FastAPI Backend API first
    try:
        from utils.api_client import backend_health, api_predict_it_risk
        api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
        if backend_health(api_base):
            api_res = api_predict_it_risk(features_dict, base_url=api_base)
            if api_res and "risk_score" in api_res:
                return api_res
    except Exception:
        pass

    # 2. Local XGBoost Engine Fallback
    model, f_names, f_types = load_it_model()
    if not model or not f_names:
        return {"risk_score": 50.0, "risk_level": "Medium"}

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
    
    return {
        "risk_score": round(score, 1),
        "risk_level": get_risk_level(score)
    }

def predict_non_it_risk(features_dict):
    """
    Predicts risk for Non-IT projects using ML model pipeline with fallback to dynamic risk telemetry.
    """
    # 1. Try FastAPI Backend API first
    try:
        from utils.api_client import backend_health, api_predict_non_it_risk
        api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
        if backend_health(api_base):
            api_res = api_predict_non_it_risk(features_dict, base_url=api_base)
            if api_res and "risk_score" in api_res and api_res["risk_score"] > 0:
                return api_res
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

    return {
        "risk_score": round(score, 1),
        "risk_level": get_risk_level(score)
    }
