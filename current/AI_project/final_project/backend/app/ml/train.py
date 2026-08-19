import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from app.ml.feature_extractor import FEATURE_NAMES
from app.ml.synthetic_data import generate_synthetic_dataset
from app.core.config import settings

def train_and_evaluate_models(data_path: str = None, save_model: bool = True):
    print("==================================================")
    print("INITIATING AI PROJECT RISK MODEL TRAINING PIPELINE")
    print("==================================================")
    
    # 1. Load or Generate Dataset
    if data_path and os.path.exists(data_path):
        print(f"Loading data from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print("Generating realistic synthetic training data with non-linear dependencies...")
        df = generate_synthetic_dataset(num_samples=2500, random_seed=42)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/project_risk_training_dataset.csv", index=False)
        print("Saved dataset to data/project_risk_training_dataset.csv")

    X = df[FEATURE_NAMES]
    y = df["is_high_risk"]
    y_continuous = df["true_risk_probability"]

    # 2. Stratified Train / Test Split
    X_train, X_test, y_train, y_test, y_prob_train, y_prob_test = train_test_split(
        X, y, y_continuous, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42))
        ]),
        "Gradient Boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(n_estimators=120, max_depth=4, learning_rate=0.08, random_state=42))
        ])
    }

    results = {}
    best_model_name = None
    best_roc_auc = -1.0
    best_pipeline = None

    print("\n--- MODEL BENCHMARKING & EVALUATION ---")
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm
        }

        print(f"\nModel: {name}")
        print(f"  • Accuracy : {acc:.4f}")
        print(f"  • Precision: {prec:.4f}")
        print(f"  • Recall   : {rec:.4f}")
        print(f"  • F1-Score : {f1:.4f}")
        print(f"  • ROC-AUC  : {auc:.4f}")

        if auc > best_roc_auc:
            best_roc_auc = auc
            best_model_name = name
            best_pipeline = pipeline

    print(f"\nBest Selected Model: {best_model_name} (ROC-AUC: {best_roc_auc:.4f})")

    # Feature importances calculation
    feature_importances = {}
    classifier = best_pipeline.named_steps["classifier"]
    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
        for f_name, imp in zip(FEATURE_NAMES, importances):
            feature_importances[f_name] = round(float(imp), 4)
    elif hasattr(classifier, "coef_"):
        coefs = np.abs(classifier.coef_[0])
        norm_coefs = coefs / np.sum(coefs)
        for f_name, imp in zip(FEATURE_NAMES, norm_coefs):
            feature_importances[f_name] = round(float(imp), 4)

    # Sort feature importances descending
    sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    metadata = {
        "model_type": best_model_name,
        "features": FEATURE_NAMES,
        "feature_importances": sorted_importances,
        "metrics": results[best_model_name],
        "all_model_evaluations": results,
        "training_samples": len(df),
        "test_samples": len(X_test),
        "data_disclaimer": "Trained on synthetic project historical telemetry for demonstration and validation. Production usage requires continuous integration of real enterprise project tracking data."
    }

    if save_model:
        os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
        joblib.dump(best_pipeline, settings.MODEL_PATH)
        print(f"Saved model binary to {settings.MODEL_PATH}")

        with open(settings.METADATA_PATH, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved model metadata to {settings.METADATA_PATH}")

    return best_pipeline, metadata

if __name__ == "__main__":
    train_and_evaluate_models()
