from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "heart.csv"
MODELS = BASE / "models"

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope",
    "ca", "thal"
]


def main():
    print("=" * 65)
    print("CARDIOVEYRA - MODEL TRAINING")
    print("An Intelligent Machine Learning Framework for Heart Disease Prediction")
    print("=" * 65)

    # 1. Load dataset
    if not DATA.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA}")

    df = pd.read_csv(DATA)

    required_columns = FEATURES + ["target"]
    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in heart.csv: {missing}")

    df = df.dropna(subset=required_columns)

    X = df[FEATURES]
    y = df["target"]

    # 2. 80:20 split - matches the project methodology
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=0
    )

    print(f"\nDataset records : {len(df)}")
    print(f"Training records: {len(X_train)}")
    print(f"Testing records : {len(X_test)}")
    print("Split           : 80% training / 20% testing")

    # 3. Models
    candidates = {
        # Project methodology: K = 7
        "KNN": KNeighborsClassifier(n_neighbors=7),

        "Logistic Regression": LogisticRegression(
            solver="newton-cg",
            max_iter=1000
        ),

        "Naive Bayes": GaussianNB(),

        # No probability=True: avoids the warning and is not needed
        # because this script only uses predict().
        "SVM": SVC(
            kernel="linear",
            random_state=0
        ),

        "Decision Tree": DecisionTreeClassifier(
            random_state=0
        ),

        # Final model: 100 estimators
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=0
        ),
    }

    rows = []
    fitted = {}

    print("\n" + "=" * 65)
    print("MODEL PERFORMANCE")
    print("=" * 65)

    for name, model in candidates.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        fitted[name] = model

        accuracy = accuracy_score(y_test, pred)
        precision = precision_score(
            y_test, pred, zero_division=0
        )
        recall = recall_score(
            y_test, pred, zero_division=0
        )
        f1 = f1_score(
            y_test, pred, zero_division=0
        )

        rows.append({
            "model": name,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })

        print(
            f"{name}: "
            f"{accuracy:.4f} ({accuracy * 100:.2f}%)"
        )

    # 4. Save model files
    MODELS.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        fitted["Random Forest"],
        MODELS / "heartrf.joblib"
    )

    joblib.dump(
        fitted["Random Forest"],
        MODELS / "best_heart_model.pkl"
    )

    joblib.dump(
        FEATURES,
        MODELS / "selected_features.pkl"
    )

    # 5. Save metrics
    results = pd.DataFrame(rows)

    results.to_csv(
        MODELS / "metrics.csv",
        index=False
    )

    with open(
        MODELS / "metrics.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write("CARDIOVEYRA\n")
        f.write(
            "An Intelligent Machine Learning Framework "
            "for Heart Disease Prediction\n"
        )
        f.write("=" * 65 + "\n\n")

        f.write(
            f"Dataset: UCI Heart Disease (Cleveland), "
            f"{len(df)} rows\n"
        )
        f.write("Features: 13\n")
        f.write("Split: 80% training / 20% testing\n")
        f.write("random_state: 0\n")
        f.write("KNN neighbors: 7\n")
        f.write("Random Forest estimators: 100\n\n")

        f.write("MODEL RESULTS\n")
        f.write("-" * 65 + "\n")

        for row in rows:
            f.write(
                f"{row['model']:<22}"
                f"Accuracy={row['accuracy']:.4f}  "
                f"Precision={row['precision']:.4f}  "
                f"Recall={row['recall']:.4f}  "
                f"F1={row['f1']:.4f}\n"
            )

        f.write("\nFinal model: Random Forest (100 estimators)\n")

    print("\n" + "=" * 65)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 65)
    print(f"Final model saved to: {MODELS / 'heartrf.joblib'}")


if __name__ == "__main__":
    main()
