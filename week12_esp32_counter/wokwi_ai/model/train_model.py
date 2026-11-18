"""Reproduce training of the actual Wokwi logistic regression model."""
from pathlib import Path
import csv, json
from sklearn.linear_model import LogisticRegression
folder = Path(__file__).resolve().parent
with (folder / "samples.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
X = [[float(r["distance_cm"])] for r in rows if r["split"] == "train"]
y = [int(r["actual_target"]) for r in rows if r["split"] == "train"]
model = LogisticRegression(solver="liblinear", C=1.0, random_state=42).fit(X, y)
weights = {
    "intercept": float(model.intercept_[0]),
    "distance_weight": float(model.coef_[0][0]),
    "training_rows": len(X)
}
(folder / "model_weights.json").write_text(
    json.dumps(weights, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(weights)
