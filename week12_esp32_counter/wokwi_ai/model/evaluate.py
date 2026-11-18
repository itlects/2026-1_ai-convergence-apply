"""Evaluate independent test rows without extra packages."""
from pathlib import Path
import csv, json, math
folder = Path(__file__).resolve().parent
w = json.loads((folder/"model_weights.json").read_text(encoding="utf-8"))
with (folder/"samples.csv").open(encoding="utf-8", newline="") as f:
    rows = [r for r in csv.DictReader(f) if r["split"]=="test"]
def confidence(distance_cm):
    z=w["intercept"]+w["distance_weight"]*distance_cm
    return 1.0/(1.0+math.exp(-z))
print("threshold TP FP FN TN precision recall F1")
for t in (0.30,0.40,0.50,0.60,0.70,0.80):
    tp=fp=fn=tn=0
    for row in rows:
        actual=int(row["actual_target"])
        pred=int(confidence(float(row["distance_cm"])) >= t)
        if actual==1 and pred==1: tp+=1
        elif actual==0 and pred==1: fp+=1
        elif actual==1 and pred==0: fn+=1
        else: tn+=1
    prec=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    f1=2*prec*recall/(prec+recall) if prec+recall else 0
    print(f"{t:.2f} {tp:2} {fp:2} {fn:2} {tn:2} {prec:.3f} {recall:.3f} {f1:.3f}")
