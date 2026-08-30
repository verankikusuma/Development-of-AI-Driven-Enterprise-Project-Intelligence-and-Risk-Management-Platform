import os
from app.ml.synthetic_data import generate_synthetic_dataset

def main():
    print("Generating comprehensive synthetic dataset for ML model training...")
    os.makedirs("data", exist_ok=True)
    df = generate_synthetic_dataset(num_samples=3000, random_seed=42)
    output_path = "data/project_risk_training_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} project telemetry records with 17 risk features.")
    print(f"File saved to {output_path}")

if __name__ == "__main__":
    main()
