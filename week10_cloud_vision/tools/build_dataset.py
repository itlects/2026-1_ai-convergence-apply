"""Fruits-360(100x100, CC BY-SA 4.0)에서 4개 클래스 x 20장을 골라 10주차 데이터셋을 만든다."""
import csv, random, re, shutil, sys, zipfile
from pathlib import Path

SRC = Path(sys.argv[1])            # fruits-360-100x100/Test
OUT = Path(sys.argv[2])            # week10_cloud_vision/dataset
CLASSES = {"apple": "Apple Red 1", "banana": "Banana 1",
           "orange": "Orange 1", "lemon": "Lemon 1"}
PER_CLASS = 20

def num(p):
    return int(re.findall(r"\d+", p.stem)[-2]) if p.stem.startswith("r") else int(p.stem.split("_")[0])

img_root = OUT / "week10_fruits" / "images"
if img_root.exists():
    shutil.rmtree(img_root)
rows = []
for cls, folder in CLASSES.items():
    files = sorted((SRC / folder).glob("*.jpg"), key=lambda p: (p.stem.startswith("r"), num(p)))
    step = len(files) / PER_CLASS
    picked = [files[int(i * step)] for i in range(PER_CLASS)]
    (img_root / cls).mkdir(parents=True)
    for i, f in enumerate(picked, 1):
        rel = f"images/{cls}/{cls}_{i:02d}.jpg"
        shutil.copy(f, OUT / "week10_fruits" / rel)
        rows.append({"path": rel, "true_label": cls, "source": f"{folder}/{f.name}"})

base = OUT / "week10_fruits"
with open(base / "labels.csv", "w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["path", "true_label"])
    w.writeheader()
    w.writerows({"path": r["path"], "true_label": r["true_label"]} for r in rows)
with open(base / "SOURCE.csv", "w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["path", "source"])
    w.writeheader()
    w.writerows({"path": r["path"], "source": r["source"]} for r in rows)
(base / "ATTRIBUTION.txt").write_text(
    "Images: Fruits-360 dataset (100x100 branch), Mihai Oltean, 2017-.\n"
    "https://github.com/fruits-360/fruits-360-100x100\n"
    "License: CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)\n"
    "Changes: 4 classes x 20 images selected and renamed for the Week10 class.\n"
    "This subset is distributed under the same CC BY-SA 4.0 license.\n", encoding="utf-8")

# 워크북 2와 같은 규칙: 클래스별 seed 42 셔플 후 70/15/15
rng = random.Random(42)
split_rows = []
for cls in sorted(CLASSES):
    items = [r for r in rows if r["true_label"] == cls]
    rng.shuffle(items)
    n = len(items); n_train = int(n * 0.70); n_val = int(n * 0.15)
    for i, r in enumerate(items):
        s = "train" if i < n_train else ("val" if i < n_train + n_val else "test")
        split_rows.append({"path": r["path"], "true_label": cls, "split": s})
with open(base / "split_seed42.csv", "w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["path", "true_label", "split"])
    w.writeheader(); w.writerows(split_rows)

zp = OUT / "week10_fruits.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(base.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(OUT))
print(len(rows), "images ->", zp, zp.stat().st_size, "bytes")
for s in ("train", "val", "test"):
    print(s, sum(r["split"] == s for r in split_rows))
print([r["path"] for r in split_rows if r["split"] == "test"])
