"""노트북(학생용/완성본)과 실행 결과로 Notion 따라하기 페이지 마크다운을 만든다.

python3 tools/make_notion_followalong.py OUT_DIR
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1])
R = "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/main/week10_cloud_vision"
EXP = json.loads((ROOT / "tools/expected_outputs.json").read_text(encoding="utf-8"))
VIS = '<span color="orange">형식 예시 — 실제 라벨·점수는 실행할 때 달라진다</span>'


def cells(name):
    nb = json.loads((ROOT / "colab" / name).read_text(encoding="utf-8"))
    return {c["metadata"]["id"]: "".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"}


S1, C1 = cells("Week10_Workbook1_VisionAPI_Student.ipynb"), cells("Week10_Workbook1_VisionAPI_Complete.ipynb")
S2, C2 = cells("Week10_Workbook2_DataSplit_Student.ipynb"), cells("Week10_Workbook2_DataSplit_Complete.ipynb")


def fence(lang, s):
    return f"```{lang}\n{s.rstrip()}\n```"


def step(title, why, code, table, expect=None, note="", answer=None, check=None, image=None):
    out = [f"### {title}", "", why, "", fence("python", code), ""]
    if table:
        out += ["<b>코드 해설</b>", "", "| 코드 | 의미 |", "| --- | --- |"]
        out += [f"| `{c}` | {m} |" for c, m in table]
        out.append("")
    if expect:
        head = "<b>▶ 실행 결과 미리 보기</b>" + (f" — {note}" if note else "")
        out += [head, "", fence("text", expect), ""]
    if image:
        out += [f"![{title}]({R}/{image})", ""]
    if check:
        out += [f"- [ ] {c}" for c in check]
        out.append("")
    if answer:
        out += ['<toggle heading="h4">', "빈칸 정답 보기 (먼저 스스로 채워 본 뒤 열기)", "", fence("python", answer), "</toggle>", ""]
    return "\n".join(out)


PREP_TABLE = [
    ("DATA_FOLDER_ID = \"1Is7...\"", "강의 Drive의 `04_데이터_과일80장` 폴더 ID. 이 폴더를 통째로 내려받는다"),
    ("gdown.download_folder(id=..., output=...)", "공유 링크로 열린 Drive 폴더를 Colab 저장소로 복사 (가장 빠름)"),
    ("DRIVE_DIR.rglob(\"week10_fruits.zip\")", "내려받은 폴더 안에서 zip 파일을 찾는다"),
    ("urllib.request.urlretrieve(GITHUB_ZIP, ...)", "Drive가 막혔을 때 GitHub에서 같은 zip을 받는다"),
    ("zipfile.ZipFile(zip_path).extractall(\".\")", "압축을 풀면 `week10_fruits/` 폴더가 생긴다"),
    ("csv.DictReader(open(...labels.csv))", "CSV 한 줄을 `{'path':..., 'true_label':...}` 사전으로 읽는다"),
    ("try: ... except Exception as e:", "실패해도 멈추지 않고 다음 방법으로 넘어가게 한다"),
]

VISION_TABLE = [
    ("get_api_key()", "① 환경변수 → ② Colab 보안 비밀 `VISION_API_KEY` → ③ `getpass` 입력창 순서로 키를 받는다. 입력 내용은 노트북에 저장되지 않는다"),
    ("base64.b64encode(...).decode(\"ascii\")", "이미지 바이트를 Base64 글자로 바꿔 JSON에 넣을 수 있게 한다"),
    ("\"features\": [{\"type\": \"LABEL_DETECTION\", \"maxResults\": ...}]", "Vision에 '라벨 검출'을 최대 N개까지 해 달라고 요청"),
    ("requests.post(VISION_URL, params={\"key\": api_key}, json=...)", "HTTPS POST. `params`는 주소 뒤 `?key=...`, `json`은 요청 본문"),
    ("range(0, len(paths), batch)", "16장씩 묶어 보낸다 (Vision은 한 요청에 최대 16장)"),
    ("r.status_code != 200 → RuntimeError", "키 오류(400), API 꺼짐(403) 등을 알기 쉬운 오류로 바꾼다"),
    ("resp.get(\"labelAnnotations\", [])", "라벨이 하나도 없으면 빈 목록"),
    ("load_cache()", "강의자가 미리 만든 `vision_cache.json`을 Drive 폴더(→ GitHub)에서 찾는다"),
    ("MODE = \"live\" / \"cache\" / \"none\"", "키가 있으면 live, 없고 캐시가 있으면 cache, 둘 다 없으면 none"),
    ("get_labels(paths)", "모드에 상관없이 같은 모양 `{경로: [{description, score}, ...]}`으로 돌려준다"),
]

COLAB_START = """<callout icon="🧑‍💻" color="blue_bg">
<b>Colab 시작하기 (처음 1번)</b>

1. 아래 '학생용 Colab' 링크 열기 → 상단 메뉴 <b>파일 › Drive에 사본 저장</b> (내 Drive에 저장해야 고친 내용이 남는다)
2. 위에서부터 셀을 하나씩 선택하고 <b>Shift + Enter</b> (셀 왼쪽 ▶ 버튼과 같음)
3. 셀 왼쪽에 숫자 `[1]`이 생기면 실행 완료, 빨간 오류가 나오면 이 페이지의 '빈칸 정답'과 '문제 해결'을 확인
4. 처음부터 다시 하고 싶으면 <b>런타임 › 세션 다시 시작</b> 후 위에서부터 다시 실행
5. 학생용 코드의 `____` 는 직접 채우는 빈칸이다. 채우기 전에는 `NameError`가 나는 것이 정상
</callout>"""

# ===================================================================== 워크북 1 Colab
wb1 = [f"""<callout icon="🧭" color="green_bg">
<b>이 페이지에서 하는 일</b> — ESP32 예제 2·3이 Cloud Vision과 주고받는 내용을 Colab에서 먼저 눈으로 확인한다. (약 20분)

[학생용 Colab 열기](https://colab.research.google.com/drive/1tIhyKu7X8yDhEFs7TYDIRB7HuOwa-Fu8) · [완성본 Colab](https://colab.research.google.com/drive/1SHS2Gcy3TYvgewOoqfpuEecDTDFkdrBO) · <mention url="https://app.notion.com/p/40db2e6bf80781129898f73fb395e733">워크북 1 (ESP32)</mention> · <mention url="https://app.notion.com/p/40db2e6bf80780f0b253edeeb0253a31">10주차 학습자료</mention>
</callout>

{COLAB_START}

![ESP32 Vision 흐름]({R}/diagrams/05_esp32_vision_flow.png)

## 따라하기 순서

| 단계 | 내용 | 빈칸 | 시간 |
| --- | --- | --- | --- |
| 0 | 라이브러리 설치 | — | 1분 |
| 1 | 데이터 준비 (Drive → Colab) | — | 2분 |
| 2 | 이미지 1장을 바이트·Base64로 보기 | 1개 | 4분 |
| 3 | 요청 JSON 만들기 | 1개 | 3분 |
| 4 | API 키 입력과 모드 확인 | — | 3분 |
| 5 | 응답 JSON 읽기 | 1개 | 4분 |
| 6 | 과일 4종 라벨 비교 | — | 3분 |
""",
    "## 0단계. 라이브러리 설치",
    step("셀 0 — gdown 설치",
         "Google Drive 폴더를 내려받는 `gdown` 도구를 설치한다. 앞의 `!`는 '파이썬이 아니라 터미널 명령'이라는 뜻이다.",
         S1["w1_install"], [("!pip -q install gdown", "pip(파이썬 패키지 설치기)로 gdown 설치, `-q`는 출력 줄이기")],
         check=["오류 없이 끝났다 (출력이 거의 없어도 정상)"]),
    "## 1단계. 데이터 준비 — Drive에 미리 올려 둔 과일 80장",
    step("셀 1 — prepare_data()",
         "실습 시간에 큰 파일을 각자 찾고 받는 시간을 줄이기 위해, 강의자가 Drive에 올려 둔 zip을 자동으로 받아 압축을 푼다. 실패하면 GitHub → 직접 업로드 순서로 넘어간다. <b>코드를 고칠 곳은 없다.</b>",
         S1["w1_prepare"], PREP_TABLE, EXP["w1_prepare"],
         check=["`이미지 수 : 80` 이 나왔다", "왼쪽 📁 파일 창에 `week10_fruits` 폴더가 생겼다 (안 보이면 새로고침)"]),
    """<callout icon="📂" color="gray_bg">
`week10_fruits/` 안에는 `images/apple/apple_01.jpg ...` (클래스별 20장), 정답표 `labels.csv`(path, true_label), 분할표 `split_seed42.csv`, 출처 `ATTRIBUTION.txt`가 들어 있다.
</callout>""",
    "## 2단계. 이미지 1장을 바이트와 Base64로 보기 (ESP32 예제 2와 같은 일)",
    step("셀 2 — 바이트 · Base64 · 이미지 표시",
         "컴퓨터에서 사진은 0~255 숫자(바이트)의 나열이다. JSON에는 글자만 넣을 수 있으므로 Base64로 바꾼다. ESP32 예제 2의 시리얼 출력과 같은 숫자가 나오는지 비교한다.",
         S1["w1_bytes"],
         [("(DATA_DIR / path).read_bytes()", "파일을 바이트 그대로 읽는다"),
          ("base64.b64encode(raw).decode(\"ascii\")", "<b>빈칸</b> — 바이트 → Base64 글자(문자열)"),
          ("raw[:3].hex(\" \").upper()", "앞 3바이트를 16진수로. JPEG는 항상 `FF D8 FF`로 시작"),
          ("len(b64) / len(raw)", "Base64는 3바이트를 4글자로 바꾸므로 약 1.33배"),
          ("Image.open(...)", "PIL로 이미지 열기, `.size`는 (가로, 세로)"),
          ("plt.imshow(img); plt.axis(\"off\")", "matplotlib로 그림 표시, 눈금 숨기기")],
         EXP["w1_bytes"], image="screens/wb1_apple02.png",
         check=["크기 4925 bytes, 첫 3바이트 FF D8 FF", "Base64 길이 6568 (ESP32 예제2 출력과 같은가?)"],
         answer='b64 = base64.b64encode(raw).decode("ascii")'),
    "## 3단계. 요청 JSON 만들기 (ESP32 예제 3의 body와 같은 구조)",
    step("셀 3 — request_body",
         "Vision에 보낼 요청 내용을 파이썬 사전(dict)으로 만든다. `json.dumps()`로 글자로 바꾸면 ESP32가 보내는 문자열과 같은 모양이 된다.",
         S1["w1_request"],
         [("\"requests\": [ {...} ]", "여러 이미지를 한 번에 보낼 수 있도록 목록 형태"),
          ("\"image\": {\"content\": b64}", "2단계에서 만든 Base64 이미지"),
          ("\"type\": \"LABEL_DETECTION\"", "<b>빈칸</b> — 사용할 Vision 기능 이름 (따옴표 포함 문자열)"),
          ("\"maxResults\": 5", "라벨을 최대 5개 받기"),
          ("json.dumps(request_body)", "사전 → JSON 문자열")],
         EXP["w1_request"], check=["`LABEL_DETECTION` 이 출력 끝부분에 보인다"],
         answer='"features": [{"type": "LABEL_DETECTION", "maxResults": 5}],'),
    "## 4단계. API 키 입력과 Vision 모드 확인",
    """<callout icon="🔑" color="yellow_bg">
셀을 실행하면 아래쪽에 <b>입력창</b>이 생긴다. 강의자가 알려 준 키를 붙여넣고 Enter → `live` 모드. 키가 없으면 그냥 Enter → `cache` 모드(강의자가 미리 저장한 결과). 키는 화면·노트북에 남지 않는다. 자주 쓰려면 왼쪽 🔑 <b>보안 비밀</b>에 이름 `VISION_API_KEY`로 저장하고 '노트북 액세스'를 켠다.
</callout>""",
    step("셀 4 — Vision 호출 함수 정의 + 모드 결정",
         "Vision을 부르는 함수(`vision_labels`), 캐시를 읽는 함수(`load_cache`), 모드에 맞게 라벨을 가져오는 함수(`get_labels`)를 만든다. <b>고칠 곳은 없다.</b> 함수 정의(`def`)는 '만들어 두기'일 뿐이고 실제 호출은 다음 셀에서 한다.",
         S1["w1_vision"], VISION_TABLE, EXP["w1_vision"] if "w1_vision" in EXP else None,
         note="cache 모드 예시",
         check=["`Vision 모드:` 가 live 또는 cache 로 나왔다", "none 이면: 키를 다시 입력하거나 강의자에게 캐시 준비 여부 확인"]),
    "## 5단계. 응답 JSON 읽기 — 이미지 1장",
    step("셀 5 — 응답 원문과 라벨 표",
         "live 모드는 Vision의 실제 응답을, cache 모드는 저장된 결과를 같은 모양으로 보여 준다. 응답 안에서 `responses[0].labelAnnotations` 목록을 꺼내 순위표로 출력한다.",
         S1["w1_one"],
         [("requests.post(..., json=request_body)", "3단계에서 만든 요청을 그대로 보낸다"),
          ("r.status_code", "200이면 성공. 400 = 키 오류, 403 = API 사용 안 함"),
          ("json.dumps(response, indent=1)[:600]", "응답 원문을 보기 좋게 앞부분만 출력"),
          ("response[\"responses\"][0][\"labelAnnotations\"]", "첫 번째 이미지의 라벨 목록"),
          ("score = a[\"score\"]", "<b>빈칸</b> — 라벨의 신뢰도(0~1) 꺼내기"),
          ("f\"{i:>3}   {name:<24}{score:.3f}\"", "f-문자열: `>3` 오른쪽 정렬 3칸, `<24` 왼쪽 정렬 24칸, `.3f` 소수 셋째 자리")],
         EXP["w1_one"], note=VIS,
         check=["응답 JSON에서 `description`, `score` 를 찾았다", "1위 라벨이 과일 이름인지 확인했다"],
         answer='score = a["score"]'),
    "## 6단계. 과일 4종의 라벨 비교 (ESP32 예제 3과 같은 4장)",
    step("셀 6 — 4장 라벨 비교",
         "클래스별 1장씩 4장의 라벨을 비교한다. 어떤 단어가 그 과일을 가리키는지, 어떤 라벨이 헷갈리게 하는지 찾는 것이 워크북 2 '매핑 규칙'의 출발점이다.",
         S1["w1_four"],
         [("get_labels(four)", "4장을 한 번에 요청 (live) 또는 캐시에서 꺼냄"),
          ("plt.subplots(1, 4)", "그림 4칸을 가로로 만들기"),
          ("labels4.get(p, [])[:5]", "라벨 상위 5개 (없으면 빈 목록)"),
          ("\", \".join(...)", "라벨들을 쉼표로 이어 한 줄로 출력")],
         EXP["w1_four"], note=VIS, image="screens/wb1_four_images.png",
         check=["lemon 라벨 중 orange 와 헷갈릴 만한 단어(예: Citrus)를 찾았다", "1위가 과일 이름이 아닌 이미지를 찾았다"]),
    f"""## 정리 질문

![score와 accuracy]({R}/diagrams/08_confusion_accuracy.png)

| 질문 | 내 답 |
| --- | --- |
| apple_02.jpg의 크기와 Base64 길이는? ESP32 예제2와 같은가? |  |
| Vision의 1위 라벨이 과일 이름이 아닌 이미지와 그 라벨은? |  |
| lemon 사진의 라벨 중 orange와 헷갈릴 수 있는 것은? |  |
| `score 0.93`은 "93% 정확하다"는 뜻인가? 이유는? |  |

## 문제 해결

| 증상 | 해결 |
| --- | --- |
| `NameError: name '____' is not defined` | 빈칸을 아직 안 채움 → 이 페이지의 '빈칸 정답 보기' |
| `NameError: name 'b64' is not defined` (3단계) | 2단계 셀이 오류로 끝남 → 2단계를 고치고 다시 실행 |
| `Drive 다운로드 실패 → ...` 후 `GitHub` 으로 성공 | 정상 (자동으로 다른 경로 사용) |
| `FileNotFoundError: week10_fruits.zip` | 두 경로 모두 실패 → Drive 데이터 폴더에서 zip을 받아 왼쪽 파일 창에 끌어다 놓기 |
| `RuntimeError: API key not valid` | 키 앞뒤 공백, 다른 키 → 셀 4 다시 실행 후 정확히 붙여넣기 |
| `RuntimeError: ... has not been used ... or it is disabled` (403) | 프로젝트에서 Vision API가 꺼져 있음 → 강의자에게 알리기 |
| 입력창이 안 보임 | 셀 출력 맨 아래로 스크롤, 또는 셀을 다시 실행 |

다음: <mention url="https://app.notion.com/p/40db2e6bf80781129898f73fb395e733">워크북 1 (ESP32)</mention> 예제 2·3 → 워크북 2 Colab 따라하기
"""]

# ===================================================================== 워크북 2 Colab
vis_extra = S2["w2_vision"].split("    return {}\n", 1)[1].strip()
wb2 = [f"""<callout icon="🧭" color="green_bg">
<b>이 페이지에서 하는 일</b> — 과일 80장을 학습·검증·시험 데이터로 나누고, Cloud Vision + 매핑 규칙과 kNN(직접 학습)의 정확도를 <b>같은 시험 데이터</b>로 비교한다. (약 60분)

[학생용 Colab 열기](https://colab.research.google.com/drive/1iin_lR6GqiFfcDqeacl2pfcBwWOEJAP6) · [완성본 Colab](https://colab.research.google.com/drive/1TkIwVpEQSHoEnCqQVdQQbcirZmyYB2lT) · <mention url="https://app.notion.com/p/40db2e6bf80780f0b253edeeb0253a31">10주차 학습자료</mention> · <mention url="https://app.notion.com/p/40db2e6bf80781129898f73fb395e733">워크북 1 (ESP32)</mention>
</callout>

{COLAB_START}

<callout icon="📌" color="gray_bg">
<b>미리 보기 읽는 법</b> — 1~3단계, 8~9단계(kNN)는 seed 42로 고정되어 <b>누구나 같은 값</b>이 나온다. <span color="orange"><b>4~7단계(Vision)는 형식 예시</b></span>이며 실제 값은 실행할 때 달라진다.
</callout>

![전체 흐름]({R}/diagrams/01_week10_overview.png)

## 따라하기 순서

| 단계 | 내용 | 빈칸 | 시간 |
| --- | --- | --- | --- |
| 0~1 | 설치, 데이터 준비 | — | 3분 |
| 2 | 데이터 살펴보기 | — | 3분 |
| 3 | 층화 분할 (train/val/test) | ① ② | 8분 |
| 4 | Vision 준비 (키·캐시) | — | 3분 |
| 5 | 매핑 규칙 정의 | ③ ④ | 8분 |
| 6 | val로 규칙 고르기 | ⑤ | 6분 |
| 7 | test 1회 평가 + 혼동행렬, ESP32용 코드 출력 | — | 6분 |
| 8 | kNN 직접 학습 (특징 → 2특징 → 6특징) | ⑥ ⑦ | 15분 |
| 9 | 비교와 데이터 누수 점검 | — | 5분 |
""",
    "## 0~1단계. 설치와 데이터 준비",
    """셀 0(`!pip -q install gdown`)과 셀 1(`prepare_data()`)은 <mention url="https://app.notion.com/p/415b2e6bf80781fca925db03e3e200f4">워크북 1 Colab 따라하기</mention>의 0·1단계와 <b>같은 코드</b>다. 그대로 실행한다.""",
    "<b>▶ 실행 결과 미리 보기</b>\n\n" + fence("text", EXP["w2_prepare"]),
    "## 2단계. 데이터 살펴보기",
    step("셀 2 — 클래스별 개수와 샘플",
         "학습 전에 데이터를 눈으로 확인하는 습관을 들인다. 클래스마다 개수가 같은지(균형), 사진이 어떻게 생겼는지 본다.",
         S2["w2_look"],
         [("Counter(r[\"true_label\"] for r in rows)", "정답별 개수 세기"),
          ("plt.subplots(4, 6)", "4행(클래스) x 6열(샘플) 그림판"),
          ("[r[\"path\"] for r in rows if r[\"true_label\"] == c][:6]", "리스트 컴프리헨션: 클래스 c의 경로 중 앞 6개")],
         EXP["w2_look"], image="screens/wb2_samples.png",
         check=["4개 클래스 모두 20장", "같은 과일을 돌려 가며 찍은 사진이라 서로 비슷하다는 점을 확인"]),
    f"## 3단계. 학습·검증·시험 데이터 나누기 (층화 분할)\n\n![데이터 분할]({R}/diagrams/07_data_split.png)",
    step("셀 3 — stratified_split()",
         "클래스마다 따로 섞은 뒤 앞에서부터 70%(14장) → train, 15%(3장) → val, 나머지(3장) → test로 자른다. 클래스 비율이 세 데이터에서 똑같이 유지된다(층화). 마지막에 겹침이 없는지, ESP32 예제4의 test 목록과 같은지 확인하고 CSV로 저장한다.",
         S2["w2_split"],
         [("defaultdict(list)", "없는 키를 쓰면 빈 목록을 자동으로 만들어 주는 사전 → 클래스별로 모으기"),
          ("random.Random(seed)", "시드를 고정한 난수 생성기. 같은 seed면 항상 같은 순서로 섞인다"),
          ("for label in sorted(groups):", "클래스 이름 순서(apple, banana, lemon, orange)로 처리 → 결과 고정"),
          ("rng.shuffle(items)", "클래스 안에서 순서 섞기"),
          ("int(n * train_ratio)", "<b>빈칸 ①</b> — 20 x 0.70 = 14 (int는 소수점 버림)"),
          ("int(n * val_ratio)", "<b>빈칸 ②</b> — 20 x 0.15 = 3"),
          ("items[:n_train] / [n_train:n_train+n_val] / [n_train+n_val:]", "슬라이싱으로 앞 14 / 다음 3 / 나머지 3"),
          ("assert len(all_paths) == len(set(all_paths)) == len(rows)", "중복이 없고 80장이 모두 들어갔는지 검사 (틀리면 오류)"),
          ("csv.DictWriter(...).writerows(rs)", "train.csv, val.csv, test.csv 저장")],
         EXP["w2_split"],
         check=["56 / 12 / 12, 클래스별 14 / 3 / 3", "`ESP32 예제4의 시험 데이터와 동일: True`", "(도전) seed를 7로 바꿔 실행 → 목록이 바뀌는지 확인 후 42로 되돌리기"],
         answer="n_train = int(n * train_ratio)\nn_val = int(n * val_ratio)"),
    "## 4단계. Cloud Vision 준비 — API 키 또는 캐시",
    f"""이 셀의 앞부분(`get_api_key`, `vision_labels`, `load_cache`, `get_labels`)은 <mention url="https://app.notion.com/p/415b2e6bf80781fca925db03e3e200f4">워크북 1 Colab 따라하기</mention> 4단계와 같다. 마지막에 아래 코드가 추가되어 <b>val 12장 + test 12장 = 24장만</b> Vision으로 보낸다(train은 Vision을 학습시키지 않으므로 필요 없음 → 비용·시간 절약).

{fence("python", vis_extra)}

<b>▶ 실행 결과 미리 보기</b> — {VIS}

{fence("text", EXP["w2_vision"])}""",
    f"## 5단계. 매핑 규칙 정의\n\n![라벨 매핑]({R}/diagrams/06_label_mapping.png)",
    step("셀 5 — 규칙 A, 규칙 B, accuracy()",
         "Vision의 자유로운 라벨을 우리 4개 클래스로 바꾸는 규칙 두 가지와, 정확도를 직접 계산하는 함수를 만든다. 마지막 몇 줄은 그림의 예 2(lemon 사진)로 손 계산한 결과와 같은지 확인한다.",
         S2["w2_rules"],
         [("KEYWORDS = {...}", "클래스마다 '이 단어가 라벨에 들어 있으면 그 클래스'로 볼 키워드 목록"),
          ("rule_exact(labels)", "규칙 A: 1위 라벨이 클래스 이름과 똑같을 때만 인정"),
          ("lab[\"score\"] < min_score", "<b>빈칸 ③</b> — 점수가 기준보다 낮으면 `continue`(건너뛰기)"),
          ("any(w in desc for w in words)", "키워드 중 하나라도 라벨 글자 안에 들어 있으면 True"),
          ("lab[\"score\"] > best_score", "더 높은 점수의 클래스로 바꾼다 → 최고 점수 클래스 선택"),
          ("correct / len(y_true)", "<b>빈칸 ④</b> — 정확도 = 맞힌 수 ÷ 전체"),
          ("zip(y_true, y_pred)", "정답과 예측을 한 쌍씩 묶기")],
         EXP["w2_rules"],
         check=["MIN_SCORE 0.5일 때 lemon 사진이 orange로 잘못 분류되는 이유를 설명할 수 있다"],
         answer='if lab["score"] < min_score:\n    continue\n...\nreturn correct / len(y_true)'),
    f"## 6단계. 검증(val) 데이터로 규칙 고르기\n\n![val과 test 사용 순서]({R}/diagrams/09_val_test_workflow.png)",
    step("셀 6 — 후보 규칙 비교",
         "<b>test는 아직 보지 않는다.</b> 규칙 A와 규칙 B(MIN_SCORE 0.5~0.9)를 val 12장으로 평가해 가장 정확한 규칙을 고른다. 동점이면 먼저 나온 후보를 고른다.",
         S2["w2_select"],
         [("lambda L: rule_exact(L)", "이름 없는 짧은 함수. 라벨 목록 L을 받아 예측 클래스를 돌려준다"),
          ("lambda L, ms=ms: rule_keywords(L, ms)", "`ms=ms`로 반복문의 현재 값을 고정 (안 하면 모두 마지막 값 0.9가 됨)"),
          ("max(acc for acc, _, _ in results)", "<b>빈칸 ⑤</b> — 후보들의 val 정확도 중 최댓값"),
          ("next((n, r) for a, n, r in results if a == best_acc)", "최댓값을 가진 첫 번째 후보 꺼내기")],
         EXP["w2_select"], note=VIS,
         check=["선택한 규칙 이름과 val 정확도를 기록했다"],
         answer="best_acc = max(acc for acc, _, _ in results)"),
    "## 7단계. 시험(test) 데이터로 단 1번 평가",
    step("셀 7 — test 정확도와 혼동행렬",
         "고른 규칙으로 test 12장을 평가한다. 결과가 마음에 들지 않아도 <b>규칙을 다시 고치지 않는다.</b> 틀린 이미지의 라벨을 보고 이유를 분석한다.",
         S2["w2_test"],
         [("accuracy_score(y_test, vision_pred)", "scikit-learn의 정확도 함수 (5단계 accuracy()와 같은 값)"),
          ("confusion_matrix(y, pred, labels=names)", "행 = 정답, 열 = 예측 순서를 `names`로 고정한 개수 표"),
          ("ConfusionMatrixDisplay(cm, ...).plot()", "혼동행렬을 색칠된 그림으로 표시"),
          ("LABELS[r[\"path\"]][:4]", "틀린 이미지의 Vision 라벨 상위 4개 → 왜 틀렸는지 근거")],
         EXP["w2_test"], note=VIS, image="screens/wb2_confusion_example.png",
         check=["test 정확도, 틀린 이미지와 이유를 기록했다"]),
    step("셀 8 — ESP32 예제4로 옮겨 적을 코드 출력",
         "선택한 규칙을 C++ 코드로 출력한다. 출력된 줄을 그대로 복사해 `ex4_vision_classifier.ino`의 '학생 수정 구간'에 붙여 넣는다.",
         S2["w2_export"],
         [("best_name.split(\"=\")[1]", "규칙 이름 'B 키워드 MIN_SCORE=0.5'에서 숫자 부분 꺼내기"),
          ("[\"nullptr\"] * (5 - len(KEYWORDS[c]))", "C++ 배열 칸(5칸)을 채우기 위해 남는 칸을 nullptr로")],
         EXP["w2_export"], note=VIS,
         check=["출력 코드를 예제4에 붙여 넣었다 → ESP32 BTN2로 같은 test 12장 평가"]),
    f"## 8단계. 직접 지도학습 — kNN\n\n![kNN 개념]({R}/diagrams/10_knn_concept.png)",
    step("셀 9 — 색 특징 뽑기",
         "이미지 1장을 숫자 6개(과일 픽셀의 평균 R·G·B, 표준편차 R·G·B)로 바꾼다. 흰 배경은 제외한다. 산점도에서 점 = train, 동그라미 = test 이다.",
         S2["w2_features"],
         [("np.asarray(Image.open(...).convert(\"RGB\"), dtype=float) / 255", "이미지 → (100, 100, 3) 숫자 배열, 0~1로 맞춤"),
          ("a.min(axis=2) < 0.9", "세 채널 중 가장 작은 값이 0.9보다 작으면 = 흰 배경이 아님 (과일 픽셀)"),
          ("px.mean(axis=0), px.std(axis=0)", "과일 픽셀들의 채널별 평균·표준편차"),
          ("np.concatenate([...])", "두 배열을 이어 붙여 숫자 6개로"),
          ("X[\"train\"].shape", "(56, 6) = 이미지 56장 x 특징 6개"),
          ("plt.scatter(X[:, 0], X[:, 2])", "0번 특징(평균 R)과 2번 특징(평균 B)으로 산점도")],
         EXP["w2_features"], image="screens/wb2_color_scatter.png",
         check=["산점도에서 apple과 banana 점이 겹치는 곳을 찾았다"]),
    step("셀 10 — 특징 2개(평균 R, 평균 B) kNN, k는 val로 선택",
         "k = 1, 3, 5, 7, 9 중 val 정확도가 가장 높은 k를 고르고(동점이면 작은 k), 그 모델로 test를 한 번 평가한다.",
         S2["w2_knn2"],
         [("KNeighborsClassifier(n_neighbors=k)", "가장 가까운 k개의 다수결로 분류하는 모델"),
          ("model.fit(X[\"train\"][:, cols], y[\"train\"])", "<b>빈칸 ⑥</b> — 학습: train 특징과 정답을 기억"),
          ("model.score(X[\"val\"][:, cols], y[\"val\"])", "val 정확도 (predict + accuracy를 한 번에)"),
          ("X[...][:, [0, 2]]", "모든 행에서 0번·2번 열(평균 R, 평균 B)만 사용"),
          ("knn2.predict(...)", "선택한 모델로 test 예측")],
         EXP["w2_knn2"],
         check=["val 1.000인데 test 0.833 → val 정확도가 test를 보장하지 않음을 확인"],
         answer='model.fit(X["train"][:, cols], y["train"])'),
    step("셀 11 — 특징 6개 + 표준화 kNN",
         "특징 6개를 모두 쓰고, 특징마다 크기를 맞추는 표준화(StandardScaler)를 먼저 한다.",
         S2["w2_knn6"],
         [("make_pipeline(StandardScaler(), KNeighborsClassifier(k))", "표준화 → kNN을 한 모델처럼 연결"),
          ("StandardScaler", "각 특징을 평균 0, 표준편차 1로 바꿔 거리 계산이 한 특징에 치우치지 않게 함"),
          ("knn6.predict(X[\"test\"])", "<b>빈칸 ⑦</b> — test 12장 예측")],
         EXP["w2_knn6"],
         check=["2특징보다 정확도가 올라간 이유를 산점도와 연결해 설명"],
         answer='pred6 = knn6.predict(X["test"])'),
    "## 9단계. 비교와 데이터 누수 점검",
    step("셀 12 — 세 방법 비교, train으로 평가하면?, 가장 가까운 train 이미지",
         "세 방법의 test 정확도를 한 표로 비교하고, 데이터 누수를 두 가지 방법으로 점검한다.",
         S2["w2_compare"],
         [("KNeighborsClassifier(1).fit(train).score(train)", "train으로 학습하고 train으로 평가 → 거의 항상 1.0 (의미 없는 평가)"),
          ("NearestNeighbors(n_neighbors=1).fit(X[\"train\"])", "test 이미지와 가장 가까운 train 이미지를 찾는 도구"),
          ("nn.kneighbors(..., return_distance=False)[0][0]", "가장 가까운 train 이미지의 번호")],
         EXP["w2_compare"], note="Vision 줄은 형식 예시", image="screens/wb2_nearest_train.png",
         check=["test 사진과 가장 가까운 train 사진이 거의 같다는 것을 확인", "이 데이터에서 kNN 1.000이 실제보다 부풀려진 이유를 설명"]),
    """## 빈칸 정답 한눈에 보기

<toggle heading="h4">
빈칸 ①~⑦ 정답 (모두 채워 본 뒤 확인)

| 번호 | 단계 | 정답 |
| --- | --- | --- |
| ① ② | 3 분할 | `int(n * train_ratio)`, `int(n * val_ratio)` |
| ③ | 5 규칙 B | `lab["score"] < min_score` |
| ④ | 5 정확도 | `correct / len(y_true)` |
| ⑤ | 6 규칙 선택 | `max(acc for acc, _, _ in results)` |
| ⑥ | 8 kNN 학습 | `model.fit(X["train"][:, cols], y["train"])` |
| ⑦ | 8 kNN 예측 | `knn6.predict(X["test"])` |
</toggle>

## 문제 해결

| 증상 | 해결 |
| --- | --- |
| `NameError: name '____' is not defined` | 빈칸 미입력 → 위의 '빈칸 정답 보기' |
| `NameError: name 'parts' is not defined` | 3단계 셀이 오류로 끝남 → 3단계를 고치고 아래 셀을 다시 실행 |
| `AssertionError` (3단계) | 분할 개수가 틀림 → 빈칸 ①② 확인 |
| `Vision 모드: none` | 키·캐시 없음 → 4~7단계는 건너뛰고 8단계부터 진행 (분할·kNN은 그대로 가능) |
| `RuntimeError: API key not valid` | 4단계 셀을 다시 실행하고 키를 정확히 붙여넣기 |
| 7단계 `NameError: best_rule` | 6단계가 실행되지 않음 → 6단계부터 다시 실행 |
| 그래프 한글이 □로 보임 | Colab에 한글 글꼴이 없음 → 그래프 글자는 영어로 작성됨 (정상) |

## 제출용 질문표

| 질문 | 내 답 |
| --- | --- |
| 이번 실습은 지도/비지도/강화 중 무엇이고, '분류'인 이유는? |  |
| train / val / test 장수와 클래스별 장수 |  |
| 규칙 후보 중 val로 고른 규칙과 그 val 정확도 |  |
| Vision + 규칙의 test 정확도, 틀린 이미지와 이유 |  |
| ESP32 예제4에서 나온 정확도와 같은가? 다르면 이유는? |  |
| kNN 2특징 vs 6특징의 test 정확도 차이와 이유 |  |
| val 정확도와 test 정확도가 다르게 나온 경우, 왜 그럴까? |  |
| `label.score`와 `accuracy`의 차이 (2문장) |  |
| 이 데이터에서 생길 수 있는 데이터 누수와 개선 방법 |  |

## 확장 활동 (선택)

9주차 ESP32-S3 CAM으로 찍은 과일 사진을 Colab에 올려 `labels.csv`와 같은 형식(path, true_label)으로 정답을 붙이고, 이번에 고른 규칙과 kNN을 <b>새 test 데이터</b>로 평가해 본다. 정확도가 어떻게 달라지는지, 그 이유를 3~5문장으로 정리한다.
"""]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "notion_wb1_colab.md").write_text("\n\n".join(wb1), encoding="utf-8")
(OUT / "notion_wb2_colab.md").write_text("\n\n".join(wb2), encoding="utf-8")
for f in ("notion_wb1_colab.md", "notion_wb2_colab.md"):
    print(f, len((OUT / f).read_text(encoding="utf-8")))
