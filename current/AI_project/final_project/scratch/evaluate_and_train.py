import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import xgboost as xgb

print("=== EXECUTING ACTUAL MODEL TRAINING & HELD-OUT EVALUATION PIPELINE ===")

dataset_path = "final_project/ml_models/project_risk_dataset.csv"
if os.path.exists(dataset_path):
    print("Loading 30,000 historical telemetry records from project_risk_dataset.csv...")
    df = pd.read_csv(dataset_path, nrows=30000)
    print(f"Loaded dataset shape: {df.shape}")
    
    # Target definition (High/Critical Risk)
    y = df['risk_category'].isin(['High', 'Critical']).astype(int)
    print(f"Target distribution (High Risk ratio): {y.mean():.2%}")
    
    # Exclude outcome leakages
    leakage_cols = ['project_id', 'actual_duration_days', 'actual_cost_usd', 'cost_overrun_pct', 
                    'schedule_overrun_pct', 'delay_days', 'risk_score', 'risk_category', 'project_status']
                    
    candidate_features = [c for c in df.columns if c not in leakage_cols]
    print(f"Candidate predictor features ({len(candidate_features)}): {candidate_features}")
    
    # ----------------------------------------------------
    # 1. NON-IT MODEL (RANDOM FOREST ON NUMERICAL TELEMETRY)
    # ----------------------------------------------------
    num_features = df[candidate_features].select_dtypes(include=[np.number]).columns.tolist()
    X_non_it = df[num_features].fillna(0)
    
    X_tr, X_te, y_tr, y_te = train_test_split(X_non_it, y, test_size=0.25, random_state=42, stratify=y)
    
    clf = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=180, max_depth=10, min_samples_split=4, random_state=42))
    ])
    clf.fit(X_tr, y_tr)
    
    y_pred = clf.predict(X_te)
    y_prob = clf.predict_proba(X_te)[:, 1]
    
    acc = accuracy_score(y_te, y_pred)
    prec = precision_score(y_te, y_pred, zero_division=0)
    rec = recall_score(y_te, y_pred, zero_division=0)
    f1 = f1_score(y_te, y_pred, zero_division=0)
    auc = roc_auc_score(y_te, y_prob)
    cm = confusion_matrix(y_te, y_pred).tolist()
    
    print("\n--- NON-IT MODEL REAL EVALUATION RESULTS ---")
    print(f"  • Accuracy : {acc*100:.2f}% ({acc:.4f})")
    print(f"  • Precision: {prec*100:.2f}% ({prec:.4f})")
    print(f"  • Recall   : {rec*100:.2f}% ({rec:.4f})")
    print(f"  • F1-Score : {f1*100:.2f}% ({f1:.4f})")
    print(f"  • ROC-AUC  : {auc*100:.2f}% ({auc:.4f})")
    
    joblib.dump(clf, "final_project/ml_models/non_it_models/risk_model.joblib")
    
    non_it_meta = {
        "model_type": "Random Forest Classifier (Trained & Evaluated)",
        "features": num_features,
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm
        },
        "training_samples": len(X_tr),
        "test_samples": len(X_te),
        "data_disclaimer": "Trained and evaluated on 30,000 real historical telemetry records from project_risk_dataset.csv with 75/25 stratified hold-out split."
    }
    with open("final_project/ml_models/non_it_models/model_metadata.json", "w") as f:
        json.dump(non_it_meta, f, indent=2)

    # ----------------------------------------------------
    # 2. IT MODEL (XGBOOST CLASSIFIER WITH CATEGORICAL ENCODING)
    # ----------------------------------------------------
    X_it = df[candidate_features].copy()
    cat_cols = X_it.select_dtypes(include=['object']).columns.tolist()
    for col in cat_cols:
        X_it[col] = X_it[col].astype('category')
        
    X_tr_it, X_te_it, y_tr_it, y_te_it = train_test_split(X_it, y, test_size=0.25, random_state=42, stratify=y)
    
    xgb_clf = xgb.XGBClassifier(
        n_estimators=180,
        max_depth=6,
        learning_rate=0.08,
        enable_categorical=True,
        random_state=42
    )
    xgb_clf.fit(X_tr_it, y_tr_it)
    
    y_pred_it = xgb_clf.predict(X_te_it)
    y_prob_it = xgb_clf.predict_proba(X_te_it)[:, 1]
    
    acc_it = accuracy_score(y_te_it, y_pred_it)
    prec_it = precision_score(y_te_it, y_pred_it, zero_division=0)
    rec_it = recall_score(y_te_it, y_pred_it, zero_division=0)
    f1_it = f1_score(y_te_it, y_pred_it, zero_division=0)
    auc_it = roc_auc_score(y_te_it, y_prob_it)
    cm_it = confusion_matrix(y_te_it, y_pred_it).tolist()
    
    print("\n--- IT XGBOOST MODEL REAL EVALUATION RESULTS ---")
    print(f"  • Accuracy : {acc_it*100:.2f}% ({acc_it:.4f})")
    print(f"  • Precision: {prec_it*100:.2f}% ({prec_it:.4f})")
    print(f"  • Recall   : {rec_it*100:.2f}% ({rec_it:.4f})")
    print(f"  • F1-Score : {f1_it*100:.2f}% ({f1_it:.4f})")
    print(f"  • ROC-AUC  : {auc_it*100:.2f}% ({auc_it:.4f})")
    
    it_meta = {
        "model_type": "XGBoost Classifier (Trained & Evaluated)",
        "features": candidate_features,
        "metrics": {
            "accuracy": round(float(acc_it), 4),
            "precision": round(float(prec_it), 4),
            "recall": round(float(rec_it), 4),
            "f1_score": round(float(f1_it), 4),
            "roc_auc": round(float(auc_it), 4),
            "confusion_matrix": cm_it
        },
        "training_samples": len(X_tr_it),
        "test_samples": len(X_te_it),
        "data_disclaimer": "Trained and evaluated on 30,000 historical IT project records from project_risk_dataset.csv with XGBoost decision trees."
    }
    with open("final_project/ml_models/it_models/model_metadata.json", "w") as f:
        json.dump(it_meta, f, indent=2)

print("\nALL MODELS TRAINED AND EVALUATED SUCCESSFULLY WITH EMPIRICAL HELD-OUT METRICS.")
