"""10주차 Colab 노트북 생성.

python3 tools/build_notebooks.py OUT_DIR [expected.json]
expected.json 이 있으면 '실행 결과 미리 보기'를 채운다 (tools/run_and_capture.py가 만든다).
"""
import json
import sys
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Book  # noqa: E402

OUT = Path(sys.argv[1])
EXP = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv) > 2 else {}

DATA_FOLDER_ID = "1Is7dwskGMYvOxeIRhy0QYMZejj0K8BWE"
RAW = "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/main/week10_cloud_vision"
IMG = f"{RAW}/diagrams"
NOTION = "https://app.notion.com/p/40db2e6bf80780f0b253edeeb0253a31"
VISION_NOTE = "형식 예시: 실제 Vision 라벨·점수·정확도는 실행할 때 달라집니다"

# ------------------------------------------------------------------ 공통 코드
PREPARE = f'''
# 데이터 준비: ① 강의 Google Drive 폴더 → ② GitHub → ③ 직접 업로드 순서로 시도
import csv
import json
import os
import urllib.request
import zipfile
from pathlib import Path

DATA_FOLDER_ID = "{DATA_FOLDER_ID}"   # Drive: 10주_강의자료/04_데이터_과일80장
GITHUB_ZIP = (
    "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
    "main/week10_cloud_vision/dataset/week10_fruits.zip"
)
DATA_DIR = Path("week10_fruits")      # 압축을 풀면 생기는 폴더
DRIVE_DIR = Path("week10_drive")      # Drive 폴더를 내려받는 곳
CLASSES = ["apple", "banana", "orange", "lemon"]


def prepare_data():
    """과일 80장 데이터셋을 준비하고, 어디서 받았는지 돌려준다."""
    if (DATA_DIR / "labels.csv").exists():
        return "이미 준비됨"

    zip_path, source = None, None

    # ① Google Drive 폴더 (강의자가 미리 올려 둔 파일, 가장 빠름)
    try:
        import gdown
        gdown.download_folder(id=DATA_FOLDER_ID, output=str(DRIVE_DIR), quiet=True)
        found = list(DRIVE_DIR.rglob("week10_fruits.zip"))
        if found:
            zip_path, source = found[0], "Google Drive"
    except Exception as e:
        print("Drive 다운로드 실패 →", type(e).__name__)

    # ② GitHub (Drive가 막혔을 때)
    if zip_path is None:
        try:
            urllib.request.urlretrieve(GITHUB_ZIP, "week10_fruits.zip")
            zip_path, source = Path("week10_fruits.zip"), "GitHub"
        except Exception as e:
            print("GitHub 다운로드 실패 →", type(e).__name__)

    # ③ 직접 업로드 (왼쪽 파일 창에 week10_fruits.zip 을 끌어다 놓기)
    if zip_path is None and Path("week10_fruits.zip").exists():
        zip_path, source = Path("week10_fruits.zip"), "직접 업로드"

    if zip_path is None:
        raise FileNotFoundError("week10_fruits.zip 을 왼쪽 파일 창에 업로드한 뒤 다시 실행하세요")

    with zipfile.ZipFile(zip_path) as z:
        z.extractall(".")
    return source


source = prepare_data()
rows = list(csv.DictReader(open(DATA_DIR / "labels.csv", encoding="utf-8")))
print("데이터 출처 :", source)
print("이미지 수   :", len(rows))
print("첫 3줄      :", rows[:3])
'''

VISION_FUNCS = '''
# Cloud Vision REST 호출 함수 + API 키 / 캐시 준비
import base64
import requests

VISION_URL = "https://vision.googleapis.com/v1/images:annotate"
GITHUB_CACHE = (
    "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
    "main/week10_cloud_vision/dataset/vision_cache.json"
)


def get_api_key():
    """① Colab 보안 비밀(VISION_API_KEY) → ② 입력창(getpass) 순서로 키를 받는다."""
    if os.environ.get("VISION_API_KEY"):
        return os.environ["VISION_API_KEY"]
    try:
        from google.colab import userdata
        key = userdata.get("VISION_API_KEY")
        if key:
            return key
    except Exception:
        pass
    try:
        from getpass import getpass
        return getpass("Cloud Vision API 키 (없으면 그냥 Enter): ").strip()
    except Exception:
        return ""


def vision_labels(paths, api_key, max_results=10, batch=16):
    """이미지 경로 목록 → {경로: [{description, score}, ...]} (요청 1번에 최대 16장)"""
    result = {}
    for i in range(0, len(paths), batch):
        chunk = paths[i:i + batch]
        requests_body = []
        for p in chunk:
            content = base64.b64encode((DATA_DIR / p).read_bytes()).decode("ascii")
            requests_body.append({
                "image": {"content": content},
                "features": [{"type": "LABEL_DETECTION", "maxResults": max_results}],
            })
        r = requests.post(VISION_URL, params={"key": api_key},
                          json={"requests": requests_body}, timeout=60)
        data = r.json()
        if r.status_code != 200:
            raise RuntimeError(data.get("error", {}).get("message", r.text[:200]))
        for p, resp in zip(chunk, data["responses"]):
            if "error" in resp:
                raise RuntimeError(f"{p}: {resp['error'].get('message')}")
            result[p] = [
                {"description": a["description"], "score": round(a["score"], 4)}
                for a in resp.get("labelAnnotations", [])
            ]
    return result


def load_cache():
    """강의자가 만든 vision_cache.json (Drive 폴더 → GitHub 순서)"""
    found = list(DRIVE_DIR.rglob("vision_cache.json")) + [
        p for p in [Path("vision_cache.json")] if p.exists()]
    if not found:
        try:
            urllib.request.urlretrieve(GITHUB_CACHE, "vision_cache.json")
            found = [Path("vision_cache.json")]
        except Exception:
            return None
    return json.loads(found[0].read_text(encoding="utf-8"))


API_KEY = get_api_key()
CACHE = load_cache()
if API_KEY:
    MODE = "live"
elif CACHE:
    MODE = "cache"
else:
    MODE = "none"

print("Vision 모드:", MODE)
print("  live  = API를 직접 호출 (키 있음)")
print("  cache = 강의자가 미리 저장한 Vision 결과 사용 (키 없음)")
print("  none  = Vision 단계 건너뜀 (분할·kNN 실습은 그대로 가능)")
if CACHE:
    print("캐시 정보:", CACHE["meta"])
'''

GET_LABELS = '''
def get_labels(paths):
    """모드에 맞게 라벨을 가져온다."""
    if MODE == "live":
        return vision_labels(paths, API_KEY)
    if MODE == "cache":
        return {p: CACHE["labels"][p] for p in paths}
    return {}
'''

# ================================================================== 강의자용
b = Book()
b.md(f"""
# 10주차 강의자용 — Cloud Vision 결과 캐시 만들기 (수업 전 1회)

학생이 API 키 없이도 워크북을 진행할 수 있도록, 과일 80장의 Vision 라벨을 **미리 1회 호출해 `vision_cache.json`으로 저장**하고
강의 Drive 데이터 폴더에 올린다. (80회 호출 = 월 무료 1,000건 범위 안)

![API 키 준비]({IMG}/11_api_key_setup.png)

| 순서 | 할 일 |
| --- | --- |
| 1 | Google Cloud 콘솔에서 Cloud Vision API 사용 설정 + API 키 만들기 (API 제한: Cloud Vision API) |
| 2 | 이 노트북의 셀을 위에서부터 실행 (키 입력창에 붙여넣기) |
| 3 | 마지막 셀이 Drive `04_데이터_과일80장` 폴더에 `vision_cache.json`을 올리고 gdown으로 내려받기까지 확인 |
| 4 | 수업 후 API 키 삭제 또는 사용 중지 |

> 키는 이 노트북에 저장되지 않는다. 노트북을 공유하기 전에 출력에 키가 보이지 않는지 확인한다.
""")
b.code("t_install", "!pip -q install gdown", expect="none")
b.code("t_prepare", PREPARE)
b.code("t_vision", VISION_FUNCS + "\nassert API_KEY, '강의자 노트북은 API 키가 필요합니다'\n", expect="none")
b.code("t_call", '''
# 80장 전체 호출 (16장씩 5번 요청)
import datetime

paths = [r["path"] for r in rows]
labels = vision_labels(paths, API_KEY, max_results=10)

cache = {
    "meta": {
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "feature": "LABEL_DETECTION",
        "maxResults": 10,
        "images": len(labels),
    },
    "labels": labels,
}
Path("vision_cache.json").write_text(
    json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
print("저장 완료:", len(labels), "장")
for p in paths[::20]:
    print(p, [(a["description"], a["score"]) for a in labels[p][:4]])
''', expect="none")
b.code("t_upload", '''
# Drive 데이터 폴더에 업로드 (이미 있으면 같은 파일 ID로 내용만 교체)
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

auth.authenticate_user()
drive = build("drive", "v3")
query = (f"'{DATA_FOLDER_ID}' in parents and name='vision_cache.json' "
         "and trashed=false")
found = drive.files().list(q=query, fields="files(id,name)").execute()["files"]
media = MediaFileUpload("vision_cache.json", mimetype="application/json")
if found:
    drive.files().update(fileId=found[0]["id"], media_body=media).execute()
    print("기존 파일 교체:", found[0]["id"])
else:
    f = drive.files().create(
        body={"name": "vision_cache.json", "parents": [DATA_FOLDER_ID]},
        media_body=media, fields="id").execute()
    print("새로 업로드:", f["id"])
''', expect="none")
b.code("t_verify", '''
# 학생 환경과 같은 방법(gdown 폴더 다운로드)으로 받아지는지 확인
import shutil
import gdown

shutil.rmtree("check_drive", ignore_errors=True)
gdown.download_folder(id=DATA_FOLDER_ID, output="check_drive", quiet=True)
print(sorted(p.name for p in Path("check_drive").rglob("*") if p.is_file()))
''', expect="none")
instructor = b

# ================================================================== 워크북 1 (Colab 부분)
b = Book()
b.md(f"""
# 10주차 워크북 1 — Cloud Vision API 요청·응답 이해하기 (Colab 편)

ESP32 예제 3·4가 Vision에 보내는 **요청 JSON**과 받는 **응답 JSON**을 Colab에서 먼저 눈으로 확인한다.
ESP32 시리얼 모니터에 찍히는 숫자(이미지 크기, Base64 길이, 라벨·점수)와 비교하면서 진행한다.

- 강의자료: [10주차 학습자료(Notion)]({NOTION})
- 실행: 위에서부터 `Shift+Enter`. **학생용**은 `____` 빈칸을 채워야 다음 셀이 동작한다.
- API 키: 강의자가 수업 시간에 알려 준 키를 입력창에 붙여넣는다(노트북에 저장되지 않음). 키가 없으면 Enter → 캐시 모드.

![ESP32 Vision 흐름]({IMG}/05_esp32_vision_flow.png)

## 핵심 키워드 미리 보기

| 키워드 | 뜻 |
| --- | --- |
| `gdown.download_folder(id=...)` | 공유된 Google Drive 폴더를 Colab으로 내려받기 |
| `Path.read_bytes()` | 파일을 바이트(0~255 숫자열)로 읽기 |
| `base64.b64encode()` | 바이트 → 글자(A~Z, a~z, 0~9, +, /)로 변환, 길이는 약 4/3배 |
| `LABEL_DETECTION` | Vision 기능 이름: 이미지에 어울리는 라벨 여러 개 반환 |
| `maxResults` | 받을 라벨 최대 개수 |
| `requests.post(url, params, json)` | HTTPS POST 요청 (ESP32의 `http.POST(body)`와 같은 일) |
| `labelAnnotations[i].description / .score` | 라벨 이름 / 신뢰도(0~1) |
""")
b.code("w1_install", "!pip -q install gdown", expect="none")
b.md("## 1. 데이터 준비 — Drive에 미리 올려 둔 과일 80장 내려받기")
b.code("w1_prepare", PREPARE)
b.md("""
## 2. 이미지 1장을 바이트와 Base64로 보기 (ESP32 예제 2와 같은 일)

ESP32 예제 2가 시리얼에 출력한 `크기`, `첫 3바이트`, `Base64 길이`와 같은 값이 나오는지 비교한다.
""")
b.code("w1_bytes", '''
import base64
from PIL import Image
import matplotlib.pyplot as plt

path = "images/apple/apple_02.jpg"          # ESP32 예제2·3의 첫 번째 이미지
raw = (DATA_DIR / path).read_bytes()
b64 = {{base64.b64encode(raw).decode("ascii")|____}}   # 빈칸: base64 변환

print("파일       :", path)
print("크기       :", len(raw), "bytes")
print("첫 3바이트 :", raw[:3].hex(" ").upper(), "(FF D8 FF 이면 JPEG)")
print("Base64 길이:", len(b64), "글자 =", round(len(b64) / len(raw), 2), "배")
print("Base64 앞부분:", b64[:40] + "...")

img = Image.open(DATA_DIR / path)
print("이미지 크기:", img.size)
plt.figure(figsize=(2, 2))
plt.imshow(img)
plt.axis("off")
plt.show()
''')
b.md("""
## 3. 요청 JSON 만들기 (ESP32 예제 3의 `body`와 같은 구조)

Vision은 `{"requests": [ {이미지, 기능}, ... ]}` 형태를 받는다. 한 번에 여러 장(최대 16장)을 보낼 수 있다.
""")
b.code("w1_request", '''
request_body = {
    "requests": [{
        "image": {"content": b64},
        "features": [{"type": {{"LABEL_DETECTION"|"____"}}, "maxResults": 5}],
    }]
}
text = json.dumps(request_body)
print("요청 JSON 길이:", len(text), "글자")
print(text[:70] + " ... " + text[-60:])
''')
b.md("""
## 4. API 키 준비와 모드 확인

- `live` : 키를 입력해 Vision을 직접 호출 (수업 권장)
- `cache` : 키 없이 Enter → 강의자가 미리 저장한 결과(`vision_cache.json`) 사용
- Colab 왼쪽 🔑(보안 비밀)에 `VISION_API_KEY`를 저장해 두면 입력창 없이 사용된다
""")
b.code("w1_vision", VISION_FUNCS + GET_LABELS, expect="cache 모드로 실행했을 때:\n" + "Vision 모드: cache\n  live  = API를 직접 호출 (키 있음)\n  cache = 강의자가 미리 저장한 Vision 결과 사용 (키 없음)\n  none  = Vision 단계 건너뜀 (분할·kNN 실습은 그대로 가능)\n캐시 정보: {'created': '2026-11-..', 'feature': 'LABEL_DETECTION', 'maxResults': 10, 'images': 80}")
b.md("""
## 5. 응답 JSON 살펴보기 — 이미지 1장

`live` 모드면 실제 응답 원문을, `cache` 모드면 저장된 라벨을 같은 모양으로 보여 준다.
""")
b.code("w1_one", '''
if MODE == "live":
    r = requests.post(VISION_URL, params={"key": API_KEY}, json=request_body, timeout=60)
    response = r.json()
    print("HTTP 상태 코드:", r.status_code)
elif MODE == "cache":
    response = {"responses": [{"labelAnnotations": CACHE["labels"][path][:5]}]}
    print("(cache 모드: 저장된 결과를 응답 모양으로 표시)")
else:
    response = {"responses": [{"labelAnnotations": []}]}
    print("(Vision 없음: 키 또는 캐시가 필요)")

print(json.dumps(response, ensure_ascii=False, indent=1)[:600])

print("\\n순위  description               score")
for i, a in enumerate(response["responses"][0].get("labelAnnotations", []), 1):
    name = a["description"]
    score = {{a["score"]|____}}          # 빈칸: 신뢰도 꺼내기
    print(f"{i:>3}   {name:<24}{score:.3f}")
''', note=VISION_NOTE)
b.md("""
## 6. 클래스별 1장씩 — ESP32 예제 3과 같은 4장

라벨 중 **어떤 단어가 그 과일을 가리키는지** 표시해 보자. 이것이 워크북 2의 '매핑 규칙'의 출발점이다.
""")
b.code("w1_four", '''
four = ["images/apple/apple_02.jpg", "images/banana/banana_01.jpg",
        "images/orange/orange_01.jpg", "images/lemon/lemon_01.jpg"]
labels4 = get_labels(four)

fig, axes = plt.subplots(1, 4, figsize=(10, 2.6))
for ax, p in zip(axes, four):
    ax.imshow(Image.open(DATA_DIR / p))
    ax.set_title(p.split("/")[-1], fontsize=9)
    ax.axis("off")
plt.show()

for p in four:
    top = labels4.get(p, [])[:5]
    print(p.split("/")[1].ljust(7), "→", ", ".join(f"{a['description']}({a['score']:.2f})" for a in top))
''', note=VISION_NOTE)
b.md(f"""
## 7. 정리 — score 와 accuracy 는 다르다

![score vs accuracy]({IMG}/08_confusion_accuracy.png)

| 질문 | 내 답 |
| --- | --- |
| apple_02.jpg 의 크기(bytes)와 Base64 길이는? ESP32 예제2 출력과 같은가? | |
| Vision이 준 1위 라벨이 과일 이름이 아닌 이미지는? 그 라벨은? | |
| lemon 사진의 라벨 중 orange 와 헷갈릴 수 있는 라벨은? | |
| `score 0.93` 은 "93% 정확하다"는 뜻인가? 이유는? | |

다음: ESP32 예제 3·4 (Notion 워크북 1) → 워크북 2 (데이터 분할과 평가)
""")
wb1 = b

# ================================================================== 워크북 2
b = Book()
b.md(f"""
# 10주차 워크북 2 — 데이터 분할과 분류 결과 검증

**목표**: 과일 80장을 학습(train)·검증(validation)·시험(test)으로 나누고,
① Cloud Vision(사전학습 모델) + 매핑 규칙, ② kNN(직접 지도학습) 두 방법의 정확도를 **같은 시험 데이터**로 비교한다.

- 강의자료: [10주차 학습자료(Notion)]({NOTION})
- 실행: 위에서부터 `Shift+Enter`. **학생용**은 `____` 빈칸을 채워야 다음 셀이 동작한다.
- 결과 일부(분할·kNN)는 누구나 같은 숫자가 나온다(seed 42). Vision 결과는 실행할 때 달라질 수 있다.

![전체 흐름]({IMG}/01_week10_overview.png)

## 핵심 키워드 미리 보기

| 키워드 | 뜻 |
| --- | --- |
| 지도학습 / 분류 | 정답이 있는 데이터로 학습, 정해진 범주 중 하나를 예측 |
| train / validation / test | 학습용 / 규칙·하이퍼파라미터 선택용 / 마지막 1회 평가용 |
| 층화 분할(stratified) | 클래스 비율을 유지하며 나누기 (클래스마다 70/15/15) |
| `random.Random(42)` | 시드를 고정한 난수 → 누가 실행해도 같은 분할 |
| `defaultdict(list)` | 클래스별로 행을 모으는 사전 |
| `accuracy_score(y_true, y_pred)` | 맞힌 개수 ÷ 전체 개수 |
| `confusion_matrix(y_true, y_pred, labels=...)` | 정답(행) × 예측(열) 개수 표 |
| `KNeighborsClassifier(n_neighbors=k)` | 가장 가까운 k개 이웃의 다수결 분류기 |
| `fit()` / `predict()` | 학습 / 예측 |
| 데이터 누수(leakage) | 시험 데이터 정보가 학습·선택 과정에 섞여 성능이 부풀려지는 것 |
""")
b.code("w2_install", "!pip -q install gdown", expect="none")
b.md(f"""
## 1. 데이터 준비 — Drive에 미리 올려 둔 데이터 사용

![학습 종류]({IMG}/02_learning_types.png)
""")
b.code("w2_prepare", PREPARE)
b.md("## 2. 데이터 살펴보기 — 클래스별 개수와 샘플 이미지")
b.code("w2_look", '''
from collections import Counter
from PIL import Image
import matplotlib.pyplot as plt

counts = Counter(r["true_label"] for r in rows)
print("클래스별 개수:", dict(counts))

fig, axes = plt.subplots(4, 6, figsize=(9, 6))
for i, c in enumerate(CLASSES):
    sample = [r["path"] for r in rows if r["true_label"] == c][:6]
    for j, p in enumerate(sample):
        axes[i, j].imshow(Image.open(DATA_DIR / p))
        axes[i, j].axis("off")
    axes[i, 0].set_title(c, fontsize=10, loc="left")
plt.tight_layout()
plt.show()
''')
b.md(f"""
## 3. 학습·검증·시험 데이터 나누기 (층화 분할, seed 42)

![데이터 분할]({IMG}/07_data_split.png)

클래스마다 20장을 섞은 뒤 앞에서부터 70%(14장) → train, 15%(3장) → val, 나머지(3장) → test.
""")
b.code("w2_split", '''
import random
from collections import defaultdict


def stratified_split(rows, seed=42, train_ratio=0.70, val_ratio=0.15):
    groups = defaultdict(list)
    for r in rows:
        groups[r["true_label"]].append(r)

    rng = random.Random(seed)
    parts = {"train": [], "val": [], "test": []}
    for label in sorted(groups):          # 클래스 이름 순서로 처리 (항상 같은 결과)
        items = groups[label].copy()
        rng.shuffle(items)
        n = len(items)
        n_train = {{int(n * train_ratio)|____}}
        n_val = {{int(n * val_ratio)|____}}
        parts["train"] += items[:n_train]
        parts["val"] += items[n_train:n_train + n_val]
        parts["test"] += items[n_train + n_val:]
    return parts


parts = stratified_split(rows)
for name, rs in parts.items():
    print(f"{name:<5} {len(rs):>3}장", dict(Counter(r["true_label"] for r in rs)))

# 확인 1: 겹치는 이미지가 없는가?
all_paths = [r["path"] for rs in parts.values() for r in rs]
assert len(all_paths) == len(set(all_paths)) == len(rows)
print("\\n겹치는 이미지 없음, 합계", len(all_paths), "장")

# 확인 2: 강의 자료(ESP32 예제4)의 test 12장과 같은가?
ref = list(csv.DictReader(open(DATA_DIR / "split_seed42.csv", encoding="utf-8")))
same = sorted(r["path"] for r in ref if r["split"] == "test") == sorted(r["path"] for r in parts["test"])
print("ESP32 예제4의 시험 데이터와 동일:", same)
print("test 목록:", [r["path"].split("/")[-1] for r in parts["test"]])

for name, rs in parts.items():
    with open(f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "true_label"])
        w.writeheader()
        w.writerows(rs)
''')
b.md("""
> **생각해 보기**: seed를 7로 바꾸면 개수는 같지만 목록이 바뀐다. 실험을 다시 해도 같은 결과가 나오게 하려면 seed를 고정해야 한다.

## 4. Cloud Vision 준비 — API 키 또는 캐시

비용과 시간을 아끼기 위해 Vision은 **val 12장 + test 12장 = 24장**만 호출한다 (train은 Vision을 학습시키지 않으므로 필요 없음).
""")
b.code("w2_vision", VISION_FUNCS + GET_LABELS + '''

val_paths = [r["path"] for r in parts["val"]]
test_paths = [r["path"] for r in parts["test"]]
LABELS = get_labels(val_paths + test_paths)
print("\\n라벨을 받은 이미지 수:", len(LABELS))
''', note=VISION_NOTE)
b.md(f"""
## 5. 매핑 규칙 만들기 — Vision 라벨 → 4개 클래스

![라벨 매핑]({IMG}/06_label_mapping.png)

- **규칙 A (정확히 일치)**: 1위 라벨 이름이 클래스 이름과 똑같을 때만 그 클래스, 아니면 unknown
- **규칙 B (키워드 표 + MIN_SCORE)**: score ≥ MIN_SCORE 인 라벨 중 키워드가 들어 있는 라벨의 score가 가장 높은 클래스
""")
b.code("w2_rules", '''
KEYWORDS = {
    "apple": ["apple", "mcintosh", "malus"],
    "banana": ["banana", "plantain"],
    "orange": ["orange", "tangerine", "mandarin", "clementine"],
    "lemon": ["lemon", "citron"],
}


def rule_exact(labels):
    """규칙 A: 1위 라벨이 클래스 이름과 정확히 같을 때만"""
    if labels and labels[0]["description"].lower() in CLASSES:
        return labels[0]["description"].lower()
    return "unknown"


def rule_keywords(labels, min_score=0.5):
    """규칙 B: ESP32 예제4의 mapToClass()와 같은 규칙"""
    best, best_score = "unknown", 0.0
    for lab in labels:
        if {{lab["score"] < min_score|____}}:      # 점수가 낮은 라벨은 건너뛴다
            continue
        desc = lab["description"].lower()
        for c, words in KEYWORDS.items():
            if any(w in desc for w in words) and lab["score"] > best_score:
                best, best_score = c, lab["score"]
    return best


def accuracy(y_true, y_pred):
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    return {{correct / len(y_true)|____}}


# 손으로 확인: 그림의 예 2 (lemon 사진)
example = [{"description": "Citrus", "score": 0.93},
           {"description": "Orange", "score": 0.72},
           {"description": "Lemon", "score": 0.61}]
print("규칙 A →", rule_exact(example))
print("규칙 B (MIN_SCORE 0.5) →", rule_keywords(example, 0.5))
print("규칙 B (MIN_SCORE 0.8) →", rule_keywords(example, 0.8))
''')
b.md(f"""
## 6. 검증(val) 데이터로 규칙 고르기

![val과 test 사용 순서]({IMG}/09_val_test_workflow.png)

**test는 아직 보지 않는다!** 후보마다 val 정확도를 계산해 가장 좋은 규칙을 고른다.
""")
b.code("w2_select", '''
if MODE == "none":
    print("Vision 결과가 없어 이 단계를 건너뜁니다 → 8단계(kNN)로 이동하세요")
else:
    y_val = [r["true_label"] for r in parts["val"]]
    candidates = [("A 정확히 일치", lambda L: rule_exact(L))]
    for ms in [0.5, 0.6, 0.7, 0.8, 0.9]:
        candidates.append((f"B 키워드 MIN_SCORE={ms}", lambda L, ms=ms: rule_keywords(L, ms)))

    print("후보 규칙                    val 정확도")
    results = []
    for name, rule in candidates:
        pred = [rule(LABELS[r["path"]]) for r in parts["val"]]
        acc = accuracy(y_val, pred)
        results.append((acc, name, rule))
        print(f"  {name:<26} {acc:.3f}")

    best_acc = {{max(acc for acc, _, _ in results)|____}}
    best_name, best_rule = next((n, r) for a, n, r in results if a == best_acc)   # 동점이면 먼저 나온 것
    print("\\n선택한 규칙:", best_name, "(val 정확도", round(best_acc, 3), ")")
''', note=VISION_NOTE)
b.md("""
## 7. 시험(test) 데이터로 단 1번 평가 + 혼동행렬

선택이 끝났으므로 이제 test 12장을 평가한다. 결과가 마음에 들지 않아도 **규칙을 다시 고치지 않는다.**
""")
b.code("w2_test", '''
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

if MODE != "none":
    y_test = [r["true_label"] for r in parts["test"]]
    vision_pred = [best_rule(LABELS[r["path"]]) for r in parts["test"]]
    vision_acc = accuracy_score(y_test, vision_pred)
    print(f"Vision + 규칙({best_name})  test 정확도 = {vision_acc:.3f}")

    wrong = [(r, p) for r, p in zip(parts["test"], vision_pred) if p != r["true_label"]]
    print("\\n틀린 이미지:", "(없음)" if not wrong else f"{len(wrong)}장")
    for r, p in zip(parts["test"], vision_pred):
        if p != r["true_label"]:
            top = ", ".join(f"{a['description']}({a['score']:.2f})" for a in LABELS[r["path"]][:4])
            print(f"  {r['path']:<28} 정답={r['true_label']:<7} 예측={p:<8} 라벨: {top}")

    names = CLASSES + ["unknown"]
    cm = confusion_matrix(y_test, vision_pred, labels=names)
    print("\\n혼동행렬 (행=정답, 열=예측)\\n", cm)
    ConfusionMatrixDisplay(cm, display_labels=names).plot(cmap="Blues", colorbar=False)
    plt.title("Cloud Vision + mapping rule (test)")
    plt.show()
else:
    vision_acc = None
    print("Vision 결과 없음")
''', note=VISION_NOTE)
b.md("""
### ESP32 예제 4로 옮겨 적기

아래 출력 두 줄을 `ex4_vision_classifier.ino`의 **학생 수정 구간**에 그대로 붙여 넣는다.
ESP32에서 BTN2를 누르면 같은 test 12장으로 정확도를 계산한다 (실행 시점이 다르면 Vision 점수가 조금 다를 수 있다).
""")
b.code("w2_export", '''
if MODE != "none" and best_name.startswith("B"):
    ms = float(best_name.split("=")[1])
    print(f"const float MIN_SCORE = {ms:.2f};")
    print("const char* KEYWORDS[4][5] = {")
    for c in CLASSES:
        words = [f'"{w}"' for w in KEYWORDS[c]] + ["nullptr"] * (5 - len(KEYWORDS[c]))
        print("  {" + ", ".join(words) + "},   // " + c)
    print("};")
elif MODE != "none":
    print("규칙 A가 선택됨 → 예제4는 규칙 B 구조이므로 MIN_SCORE = 0.99 처럼 엄격하게 두고 비교해 보세요")
''', note=VISION_NOTE)
b.md(f"""
## 8. 직접 지도학습: kNN 분류기 (train으로 학습)

![kNN 개념]({IMG}/10_knn_concept.png)

이미지마다 **색 특징**을 뽑는다. 흰 배경을 제외한 과일 픽셀의 평균 R·G·B, 표준편차 R·G·B → 6개 숫자.
""")
b.code("w2_features", '''
import numpy as np


def color_features(path):
    a = np.asarray(Image.open(DATA_DIR / path).convert("RGB"), dtype=float) / 255
    mask = a.min(axis=2) < 0.9          # 흰 배경(세 채널 모두 밝음) 제외
    px = a[mask]
    return np.concatenate([px.mean(axis=0), px.std(axis=0)])   # [평균R,G,B, 표준편차R,G,B]


X = {s: np.array([color_features(r["path"]) for r in parts[s]]) for s in parts}
y = {s: [r["true_label"] for r in parts[s]] for s in parts}
print("train 특징 행렬 크기:", X["train"].shape)
print("apple 첫 이미지 특징 :", np.round(X["train"][0], 3))

colors = {"apple": "red", "banana": "gold", "orange": "darkorange", "lemon": "olive"}
plt.figure(figsize=(5, 4))
for c in CLASSES:
    idx = [i for i, t in enumerate(y["train"]) if t == c]
    plt.scatter(X["train"][idx, 0], X["train"][idx, 2], c=colors[c], label=c, s=25)
plt.scatter(X["test"][:, 0], X["test"][:, 2], facecolors="none", edgecolors="k", s=70, label="test")
plt.xlabel("mean R")
plt.ylabel("mean B")
plt.legend(fontsize=8)
plt.title("Color features (train dots, test circles)")
plt.show()
''')
b.md("""
### 8-1. 특징 2개(평균 R, 평균 B)만 쓰는 kNN — k는 val로 고른다
""")
b.code("w2_knn2", '''
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def pick_k(cols, ks=(1, 3, 5, 7, 9)):
    print("  k   val 정확도")
    best = None
    for k in ks:
        model = KNeighborsClassifier(n_neighbors=k)
        {{model.fit(X["train"][:, cols], y["train"])|____}}          # 학습
        acc = model.score(X["val"][:, cols], y["val"])
        print(f"  {k}   {acc:.3f}")
        if best is None or acc > best[0]:
            best = (acc, k, model)
    return best


acc_v, k2, knn2 = pick_k([0, 2])
pred2 = knn2.predict(X["test"][:, [0, 2]])
knn2_acc = accuracy_score(y["test"], pred2)
print(f"\\n선택 k = {k2}  →  test 정확도 = {knn2_acc:.3f}  (val {acc_v:.3f}과 비교)")
''')
b.md("""
### 8-2. 특징 6개 + 표준화(StandardScaler) kNN
""")
b.code("w2_knn6", '''
best6 = None
print("  k   val 정확도")
for k in (1, 3, 5, 7, 9):
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    model.fit(X["train"], y["train"])
    acc = model.score(X["val"], y["val"])
    print(f"  {k}   {acc:.3f}")
    if best6 is None or acc > best6[0]:
        best6 = (acc, k, model)

_, k6, knn6 = best6
pred6 = {{knn6.predict(X["test"])|____}}                      # 시험 데이터 예측
knn6_acc = accuracy_score(y["test"], pred6)
print(f"\\n선택 k = {k6}  →  test 정확도 = {knn6_acc:.3f}")
print(confusion_matrix(y["test"], pred6, labels=CLASSES))
''')
b.md("""
## 9. 비교와 데이터 누수 점검
""")
b.code("w2_compare", '''
print("방법                                 학습   test 정확도")
vis = "Vision 없음" if vision_acc is None else f"{vision_acc:.3f}"
print(f"Cloud Vision + 매핑 규칙             안 함  {vis}")
print(f"kNN (평균R·B 2개, k={k2})              train  {knn2_acc:.3f}")
print(f"kNN (색 특징 6개, k={k6})              train  {knn6_acc:.3f}")

# 누수 점검 1: train으로 train을 평가하면? (시험 데이터를 쓰지 않은 '가짜' 평가)
print("\\n[점검] train 데이터로 평가한 kNN(k=1) 정확도:",
      KNeighborsClassifier(1).fit(X["train"], y["train"]).score(X["train"], y["train"]))

# 누수 점검 2: test 이미지와 가장 가까운 train 이미지
from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=1).fit(X["train"])
fig, axes = plt.subplots(2, 4, figsize=(8, 4))
for j, i in enumerate([0, 3, 6, 9]):
    tp = parts["test"][i]["path"]
    k_idx = nn.kneighbors(X["test"][i:i + 1], return_distance=False)[0][0]
    near = parts["train"][k_idx]["path"]
    axes[0, j].imshow(Image.open(DATA_DIR / tp))
    axes[0, j].set_title("test " + tp.split("/")[-1], fontsize=8)
    axes[1, j].imshow(Image.open(DATA_DIR / near))
    axes[1, j].set_title("nearest train " + near.split("/")[-1], fontsize=8)
    axes[0, j].axis("off")
    axes[1, j].axis("off")
plt.tight_layout()
plt.show()
''')
b.md("""
### 결과 해석

- train으로 train을 평가하면 거의 항상 1.0 → **보지 않은 데이터(test)** 로 평가해야 하는 이유
- 같은 과일을 회전시키며 찍은 사진이라 test와 가장 가까운 train 사진이 거의 똑같다 → 이 데이터의 kNN 정확도는 **실제보다 좋게** 나왔을 가능성이 크다
- 개선: 9주차처럼 **직접 촬영한 다른 날·다른 과일** 사진을 test로 쓰기

## 10. 제출용 질문표

| 질문 | 내 답 |
| --- | --- |
| 이번 실습은 지도/비지도/강화 중 무엇이고, '분류'인 이유는? | |
| train / val / test 장수와 클래스별 장수 | |
| 규칙 후보 중 val로 고른 규칙과 그 val 정확도 | |
| Vision + 규칙의 test 정확도, 틀린 이미지와 이유 | |
| kNN 2특징 vs 6특징의 test 정확도 차이와 이유 | |
| val 정확도와 test 정확도가 다르게 나온 경우, 왜 그럴까? | |
| `label.score`와 `accuracy`의 차이 (2문장) | |
| 이 데이터에서 생길 수 있는 데이터 누수와 개선 방법 | |
""")
wb2 = b

OUT.mkdir(parents=True, exist_ok=True)
outputs = {
    "Week10_00_Instructor_VisionCache.ipynb": instructor.build(False, EXP),
    "Week10_Workbook1_VisionAPI_Complete.ipynb": wb1.build(False, EXP),
    "Week10_Workbook1_VisionAPI_Student.ipynb": wb1.build(True, EXP),
    "Week10_Workbook2_DataSplit_Complete.ipynb": wb2.build(False, EXP),
    "Week10_Workbook2_DataSplit_Student.ipynb": wb2.build(True, EXP),
}
for name, nb in outputs.items():
    nbformat.write(nb, OUT / name)
    print("wrote", name)
