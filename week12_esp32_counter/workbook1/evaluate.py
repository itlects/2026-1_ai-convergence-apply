import argparse
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "scores.csv"


def counts(rows, threshold):
    tp = fp = fn = tn = 0
    for row in rows:
        predicted = float(row["confidence"]) >= threshold
        actual = int(row["actual_object"]) == 1
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return tp, fp, fn, tn, precision, recall, f1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DATA)
    parser.add_argument("--threshold", type=float, default=0.6)
    args = parser.parse_args()
    if not (0 <= args.threshold <= 1):
        parser.error("threshold must be in [0, 1]")
    with args.csv.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print("threshold TP FP FN TN precision recall F1")
    for t in [0.3, 0.5, 0.6, 0.7, 0.9]:
        tp, fp, fn, tn, prec, rec, f1 = counts(rows, t)
        print(f"{t:.2f} {tp:2} {fp:2} {fn:2} {tn:2} {prec:.3f} {rec:.3f} {f1:.3f}")
    tp, fp, fn, tn, prec, rec, f1 = counts(rows, args.threshold)
    print(f"Selected={args.threshold:.2f}, TP={tp}, FP={fp}, FN={fn}, TN={tn}, F1={f1:.3f}")


if __name__ == "__main__":
    main()
