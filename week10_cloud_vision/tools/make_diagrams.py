"""10주차 개념도 SVG 생성 (rsvg-convert로 PNG 변환).

python3 tools/make_diagrams.py diagrams
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
FONT = "Noto Sans CJK KR, Noto Sans KR, sans-serif"
INK, SUB, LINE = "#1d2433", "#5b6475", "#9aa3b2"
BLUE, GREEN, ORANGE, RED, PURPLE, YELLOW = "#2f6fd6", "#2e9e5b", "#e08a1e", "#d64545", "#7b4fc9", "#c99a06"
TINT = {BLUE: "#e8f0fc", GREEN: "#e6f5ec", ORANGE: "#fdf1e2", RED: "#fbe9e9",
        PURPLE: "#f1ebfb", YELLOW: "#fdf6dc", LINE: "#f2f4f7"}
CLS = {"apple": RED, "banana": YELLOW, "orange": ORANGE, "lemon": "#b5a400"}


class Svg:
    def __init__(self, w, h, title, subtitle=""):
        self.w, self.h = w, h
        self.p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                  f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
                  f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
                  '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
                  'markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                  f'fill="{INK}"/></marker></defs>']
        self.text(30, 44, title, 26, INK, "start", True)
        if subtitle:
            self.text(30, 72, subtitle, 15, SUB, "start")

    def text(self, x, y, s, size=14, color=INK, anchor="middle", bold=False):
        if isinstance(anchor, bool):
            anchor, bold = "middle", anchor
        self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
                      f'xml:space="preserve" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">'
                      f'{escape(str(s))}</text>')

    def rect(self, x, y, w, h, fill="#fff", stroke=LINE, sw=1.5, rx=10, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def box(self, x, y, w, h, color, head, lines=(), size=14):
        self.rect(x, y, w, h, TINT.get(color, "#fff"), color, 2)
        self.text(x + w / 2, y + 28, head, 16, color, "middle", True)
        for i, ln in enumerate(lines):
            self.text(x + w / 2, y + 54 + i * (size + 8), ln, size, INK)

    def arrow(self, x1, y1, x2, y2, color=INK, label="", lx=0, ly=-8, sw=2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                      f'stroke-width="{sw}" marker-end="url(#ah)"{d}/>')
        if label:
            self.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, 13, color)

    def line(self, x1, y1, x2, y2, color=LINE, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                      f'stroke-width="{sw}"{d}/>')

    def save(self, name):
        (OUT / f"{name}.svg").write_text("\n".join(self.p + ["</svg>"]), encoding="utf-8")


# ---------------------------------------------------------------- 01 전체 흐름
s = Svg(1400, 560, "10주차 전체 흐름 — 사전학습 API로 분류하고, 데이터를 나눠서 검증한다",
        "9주차: 이미지 수집 → 10주차: 분류·검증·데이터 분할 → 11주차: 직접 학습(Edge Impulse)")
xs = [30, 300, 570, 840, 1110]
heads = ["① 이미지 준비", "② Cloud Vision", "③ 매핑 규칙", "④ 평가", "⑤ 데이터 분할"]
cols = [ORANGE, BLUE, PURPLE, GREEN, RED]
body = [["과일 80장 (4종 x 20)", "Drive → Colab (gdown)", "GitHub → ESP32 (HTTPS)", "9주차 촬영 사진도 가능"],
        ["LABEL_DETECTION", "라벨 + score 여러 개", "예) Fruit 0.96", "     Apple 0.93"],
        ["자유 라벨 → 4개 클래스", "키워드 표 + MIN_SCORE", "규칙은 val로 결정", "없으면 unknown"],
        ["정답(labels.csv)과 비교", "Accuracy = 맞힌 수/전체", "혼동행렬로 오답 분석", "score ≠ accuracy"],
        ["train 70% 학습", "val 15% 규칙·k 선택", "test 15% 마지막 1회", "클래스 비율 유지(층화)"]]
for x, h, c, b in zip(xs, heads, cols, body):
    s.box(x, 110, 250, 200, c, h, b)
for i in range(4):
    s.arrow(xs[i] + 252, 210, xs[i + 1] - 4, 210)
s.rect(30, 350, 1330, 170, "#fafbfc", LINE)
s.text(60, 385, "실습 위치", 16, INK, "start", True)
s.text(60, 420, "워크북 1 (ESP32-DevKitC V4) : 예제1 회로 점검 → 예제2 Wi-Fi·HTTPS 이미지 다운로드 → 예제3 Vision 라벨 → 예제4 분류기 + LED·부저 + 정확도",
       15, INK, "start")
s.text(60, 455, "워크북 2 (Colab) : 데이터 로드 → 층화 분할 → Vision 라벨(실시간 또는 캐시) → val로 매핑 규칙 선택 → test 정확도 → kNN 직접 학습과 비교",
       15, INK, "start")
s.text(60, 490, "연결 고리 : 워크북 2에서 정한 매핑 규칙(키워드, MIN_SCORE)을 예제4 코드에 옮겨 적고, 같은 test 12장으로 ESP32에서도 정확도를 확인한다",
       15, BLUE, "start", True)
s.save("01_week10_overview")

# ---------------------------------------------------------------- 02 학습 종류
s = Svg(1400, 640, "머신러닝 학습의 종류 — 정답(레이블)이 있는가?",
        "이번 주 과일 분류는 '지도학습 · 분류' 문제이다. Cloud Vision은 이미 학습된(사전학습) 모델을 빌려 쓰는 것")
s.box(30, 110, 430, 300, BLUE, "지도학습 (Supervised)",
      ["입력 + 정답 레이블로 학습", "", "분류(Classification): 정해진 범주 중 하나", "  예) 사진 → apple / banana / ...", "회귀(Regression): 연속된 숫자 예측",
       "  예) 사진 → 무게 152g", "", "★ 10주차 실습"])
s.box(485, 110, 430, 300, GREEN, "비지도학습 (Unsupervised)",
      ["정답 없이 데이터 구조를 찾음", "", "군집(Clustering)", "  예) 비슷한 사진끼리 묶기", "차원 축소", "  예) 특징을 2차원으로 시각화", "",
       "정답표가 없을 때 사용"])
s.box(940, 110, 430, 300, ORANGE, "강화학습 (Reinforcement)",
      ["행동 → 보상을 받으며 학습", "", "정답 대신 '점수(보상)'", "  예) 게임, 로봇 제어", "", "", "", "이번 주 범위 밖"])
s.rect(30, 440, 1340, 160, TINT[PURPLE], PURPLE, 2)
s.text(60, 475, "이번 주에 쓰는 두 가지 방법", 16, PURPLE, "start", True)
s.text(60, 510, "A. Cloud Vision (사전학습 모델 사용) : Google이 수많은 이미지로 이미 학습해 둔 모델 → 우리는 학습시키지 않고 '결과를 검증'만 한다",
       15, INK, "start")
s.text(60, 545, "B. kNN 분류기 (직접 지도학습) : 우리가 가진 train 56장의 색 특징과 정답으로 직접 학습 → val로 k를 고르고 test로 평가",
       15, INK, "start")
s.text(60, 580, "두 방법 모두 같은 test 12장으로 정확도를 계산해야 공정하게 비교할 수 있다", 15, PURPLE, "start", True)
s.save("02_learning_types")

# ---------------------------------------------------------------- 05 ESP32 ↔ Vision 순서도
s = Svg(1400, 760, "ESP32에서 Cloud Vision을 호출하는 순서 (예제 2·3·4)",
        "DevKitC V4는 카메라가 없으므로 GitHub의 이미지를 내려받아 Base64로 바꾼 뒤 Vision에 보낸다")
lanes = [(170, "ESP32-DevKitC V4", BLUE), (620, "GitHub (raw 이미지)", ORANGE), (1100, "Cloud Vision API", GREEN)]
for x, name, c in lanes:
    s.rect(x - 140, 100, 280, 56, TINT[c], c, 2)
    s.text(x, 135, name, 17, c, True)
    s.line(x, 156, x, 720, c, 2, "6 6")
steps = [
    (200, 170, 620, "① HTTPS GET  images/apple/apple_02.jpg", ORANGE),
    (250, 620, 170, "② 200 OK + JPEG 4,925 bytes (FF D8 FF ...)", ORANGE),
    (380, 170, 1100, "④ HTTPS POST /v1/images:annotate?key=API키", GREEN),
    (430, 1100, 170, "⑤ 200 OK + JSON  labelAnnotations[]", GREEN),
]
for y, x1, x2, lab, c in steps:
    s.arrow(x1, y, x2 - (8 if x2 > x1 else -8), y, c, lab, 0, -10)
s.rect(30, 290, 290, 64, "#fff", BLUE, 1.5)
s.text(175, 316, "③ base64::encode(buf, len)", 14, BLUE, True)
s.text(175, 340, "4,925 bytes → 6,568 글자", 13, SUB)
s.rect(30, 470, 290, 110, "#fff", BLUE, 1.5)
s.text(175, 496, "⑥ ArduinoJson 해석", 14, BLUE, True)
s.text(175, 520, "description = \"Apple\"", 13, INK)
s.text(175, 542, "score = 0.93", 13, INK)
s.text(175, 564, "→ 매핑 규칙 → 예측 클래스", 13, PURPLE)
s.rect(30, 600, 290, 90, "#fff", BLUE, 1.5)
s.text(175, 626, "⑦ 표시", 14, BLUE, True)
s.text(175, 650, "LED(예측) + 부저(정답/오답)", 13, INK)
s.text(175, 672, "시리얼: 정확도·혼동행렬", 13, INK)
s.rect(800, 470, 570, 220, "#f6f8fa", LINE)
s.text(820, 498, "요청 JSON (예제3 body)", 14, INK, "start", True)
for i, ln in enumerate(['{"requests":[{', '  "image":{"content":"/9j/4AAQ..."},',
                        '  "features":[{"type":"LABEL_DETECTION",', '                "maxResults":5}]', '}]}']):
    s.text(820, 528 + i * 22, ln, 13, "#3b3b3b", "start")
s.text(820, 650, "응답: responses[0].labelAnnotations[i].description / .score", 13, GREEN, "start", True)
s.text(820, 674, "오류: error.message (예: API key not valid.)", 13, RED, "start")
s.save("05_esp32_vision_flow")

# ---------------------------------------------------------------- 06 라벨 매핑
s = Svg(1400, 620, "라벨 매핑 규칙 — Vision의 자유 라벨을 우리의 4개 클래스로 바꾸기",
        "score가 MIN_SCORE 이상이고 키워드가 들어 있는 라벨 중, score가 가장 높은 것의 클래스를 예측으로 한다 (예시 값)")
examples = [
    ("예 1) apple 사진", [("Fruit", .96, "-"), ("Apple", .93, "apple"), ("Mcintosh", .80, "apple")], "apple", GREEN),
    ("예 2) lemon 사진", [("Citrus", .93, "-"), ("Orange", .72, "orange"), ("Lemon", .61, "lemon")], "orange (오답)", RED),
    ("예 3) apple 사진", [("Fruit", .95, "-"), ("Red", .81, "-")], "unknown (오답)", RED),
]
for i, (head, labs, pred, c) in enumerate(examples):
    x = 30 + i * 455
    s.rect(x, 105, 430, 330, "#fafbfc", LINE)
    s.text(x + 20, 135, head, 16, INK, "start", True)
    s.text(x + 20, 165, "description", 13, SUB, "start")
    s.text(x + 210, 165, "score", 13, SUB, "start")
    s.text(x + 290, 165, "키워드 일치", 13, SUB, "start")
    for j, (d, sc, k) in enumerate(labs):
        y = 200 + j * 36
        s.text(x + 20, y, d, 15, INK, "start")
        s.text(x + 210, y, f"{sc:.2f}", 15, INK, "start")
        s.text(x + 290, y, k, 15, PURPLE if k != "-" else LINE, "start", k != "-")
    s.rect(x + 20, 350, 390, 60, TINT[c], c, 2)
    s.text(x + 215, 387, "예측 → " + pred, 17, c, True)
s.rect(30, 460, 1340, 130, TINT[PURPLE], PURPLE, 2)
s.text(60, 492, "규칙을 바꾸면 결과가 바뀐다 → 어떤 규칙이 좋은지는 검증(val) 데이터로 비교해 정한다", 16, PURPLE, "start", True)
s.text(60, 526, "키워드 예: apple=[apple, mcintosh, malus]  banana=[banana, plantain]  orange=[orange, tangerine, mandarin, clementine]  lemon=[lemon, citron]",
       14, INK, "start")
s.text(60, 556, "생각해 보기: 'Orange'는 과일 이름이면서 색 이름이다. 'Citrus'는 오렌지·레몬 둘 다에 붙는다. 'Pineapple'에는 'apple'이 들어 있다.",
       14, INK, "start")
s.save("06_label_mapping")

# ---------------------------------------------------------------- 07 데이터 분할
s = Svg(1400, 600, "학습·검증·시험 데이터 분할 — 클래스별로 70 / 15 / 15 (층화 분할, seed 42)",
        "전체 80장 = 4클래스 x 20장 → train 56장(클래스당 14) · val 12장(3) · test 12장(3)")
x0, y0, cw = 200, 120, 1000
for r, (c, col) in enumerate(CLS.items()):
    y = y0 + r * 70
    s.text(185, y + 32, c, 16, col, "end", True)
    for k in range(20):
        part = "train" if k < 14 else ("val" if k < 17 else "test")
        fill = {"train": BLUE, "val": ORANGE, "test": RED}[part]
        s.rect(x0 + k * 50, y, 44, 44, TINT[fill], fill, 1.5, 6)
for k, (name, col, n, a, b) in enumerate([("train 학습 14장", BLUE, 14, 0, 14), ("val 검증 3장", ORANGE, 3, 14, 17),
                                           ("test 시험 3장", RED, 3, 17, 20)]):
    s.text(x0 + (a + b) / 2 * 50 - 3, 420, name, 15, col, True)
s.box(30, 450, 430, 120, BLUE, "train (56장)", ["모델이 직접 보고 배우는 데이터", "kNN: 특징·정답을 저장"])
s.box(485, 450, 430, 120, ORANGE, "validation (12장)", ["규칙·하이퍼파라미터 선택", "매핑 규칙, MIN_SCORE, k 값"])
s.box(940, 450, 430, 120, RED, "test (12장)", ["모든 선택이 끝난 뒤 딱 1번 평가", "보고서에 쓰는 최종 정확도"])
s.save("07_data_split")

# ---------------------------------------------------------------- 08 혼동행렬·정확도
s = Svg(1400, 640, "정확도(Accuracy)와 혼동행렬 — 그리고 score와의 차이",
        "혼동행렬의 대각선(정답=예측)을 모두 더한 값 ÷ 전체 개수 = 정확도 (아래 숫자는 설명용 예시)")
labs = ["apple", "banana", "orange", "lemon", "unknown"]
cm = [[2, 0, 0, 0, 1], [0, 3, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 1, 2, 0]]
gx, gy, cs = 200, 160, 82
s.text(gx + cs * 2.5, gy - 40, "예측 (Vision + 매핑 규칙)", 15, SUB, True)
for j, l in enumerate(labs):
    s.text(gx + cs * j + cs / 2, gy - 12, l, 14, INK, True)
for i, l in enumerate(labs[:4]):
    s.text(gx - 12, gy + cs * i + cs / 2 + 5, l, 14, INK, "end", True)
    for j in range(5):
        v = cm[i][j]
        fill = TINT[GREEN] if i == j else (TINT[RED] if v else "#fafbfc")
        st = GREEN if i == j else (RED if v else LINE)
        s.rect(gx + cs * j, gy + cs * i, cs - 4, cs - 4, fill, st, 1.5, 6)
        s.text(gx + cs * j + cs / 2 - 2, gy + cs * i + cs / 2 + 8, v, 22, INK, True)
s.text(60, gy + cs * 2, "정답", 15, SUB, "middle", True)
s.text(gx + 200, gy + cs * 4 + 40, "Accuracy = (2+3+3+2) / 12 = 10/12 = 0.833", 18, GREEN, True)
s.box(830, 110, 540, 220, BLUE, "label.score (신뢰도)",
      ["이미지 1장, 라벨 1개에 대한 모델의 확신 정도", "0 ~ 1 사이, Vision이 알려 주는 값", "정답을 몰라도 계산됨",
       "예) 'Lemon' 0.61"])
s.box(830, 350, 540, 220, GREEN, "Accuracy (정확도)",
      ["데이터 전체에서 맞힌 비율", "정답 레이블이 있어야 계산 가능", "우리가 직접 계산하는 값",
       "예) test 12장 중 10장 정답 → 0.833"])
s.save("08_confusion_accuracy")

# ---------------------------------------------------------------- 09 val/test 사용 순서
s = Svg(1400, 520, "검증 데이터와 시험 데이터를 쓰는 순서 — 시험 데이터는 마지막에 한 번만",
        "test를 보고 규칙을 고치면 test 정확도가 실제보다 좋게 나온다 (데이터 누수, 과대평가)")
steps = [("1. 후보 만들기", ["규칙 A: 정확히 일치", "규칙 B: 키워드 표", "kNN: k = 1, 3, 5, 7"], LINE),
         ("2. val로 비교", ["후보마다 val 정확도", "가장 높은 것 선택", "(동점이면 단순한 것)"], ORANGE),
         ("3. 고정", ["선택한 규칙·k를 고정", "예제4 코드에 옮겨 적기", "이후 수정 금지"], PURPLE),
         ("4. test로 1회 평가", ["최종 정확도 보고", "혼동행렬로 오답 분석", "다음 개선은 새 데이터로"], RED)]
for i, (h, b, c) in enumerate(steps):
    x = 30 + i * 345
    s.box(x, 110, 310, 200, c if c != LINE else BLUE, h, b)
    if i < 3:
        s.arrow(x + 312, 210, x + 342, 210)
s.rect(30, 340, 1340, 140, TINT[RED], RED, 2)
s.text(60, 375, "주의: 데이터 누수(leakage)", 16, RED, "start", True)
s.text(60, 410, "· 같은 과일을 회전시키며 찍은 사진은 서로 매우 비슷하다 → train과 test에 나뉘어 들어가면 test가 '처음 보는 문제'가 아니게 된다",
       14, INK, "start")
s.text(60, 440, "· 실제 프로젝트에서는 촬영 날짜·물체(개체) 단위로 나누는 것이 더 정직하다 (워크북 2 토론 질문)", 14, INK, "start")
s.save("09_val_test_workflow")

# ---------------------------------------------------------------- 10 kNN
s = Svg(1400, 600, "kNN(k-최근접 이웃) — train 데이터로 직접 학습하는 가장 단순한 지도학습",
        "이미지 → 색 특징(평균 R·G·B 등) → 가장 가까운 k개 train 이미지의 정답으로 다수결")
s.rect(30, 100, 640, 460, "#fafbfc", LINE)
s.line(80, 520, 640, 520, INK, 2)
s.line(80, 520, 80, 130, INK, 2)
s.text(360, 552, "특징 1: 평균 R(빨강)", 14, SUB, True)
s.text(60, 120, "특징 2: 평균 B(파랑)", 14, SUB, "start", True)
import random
rng = random.Random(3)
centers = {"apple": (520, 300), "banana": (300, 420), "orange": (560, 440), "lemon": (380, 460)}
for c, (cx, cy) in centers.items():
    for _ in range(9):
        px, py = cx + rng.gauss(0, 28), cy + rng.gauss(0, 22)
        s.p.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="8" fill="{CLS[c]}" opacity="0.85"/>')
    s.text(cx, cy - 60 if c == "apple" else cy + 60 if c != "lemon" else cy + 50, c, 14, CLS[c], True)
s.p.append(f'<circle cx="470" cy="430" r="10" fill="#fff" stroke="{INK}" stroke-width="3"/>')
s.p.append(f'<circle cx="470" cy="430" r="62" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-dasharray="6 5"/>')
s.text(470, 360, "새 이미지 ? (k=5)", 14, PURPLE, True)
s.box(700, 100, 670, 220, BLUE, "학습(fit)과 예측(predict)",
      ["fit(train 특징, train 정답) : 특징과 정답을 기억", "predict(새 특징) : 가장 가까운 k개를 찾아 다수결",
       "k가 작으면 예민(과적합), 크면 둔감(과소적합)", "→ k는 val 정확도로 고른다"])
s.box(700, 340, 670, 220, GREEN, "Cloud Vision과 비교",
      ["Vision: 학습 안 함, 수천 종 라벨, 인터넷·비용 필요", "kNN: 우리 데이터로 학습, 4종만, 오프라인 무료",
       "같은 test 12장으로 두 정확도를 비교", "11주차 Edge Impulse = 더 강한 모델을 직접 학습"])
s.save("10_knn_concept")

# ---------------------------------------------------------------- 11 API 키 준비 (강의자)
s = Svg(1400, 470, "Cloud Vision API 키 준비 (강의자, 수업 전 1회)",
        "학생 개인 결제 설정 없이 수업용 키 1개를 수업 시간에만 나눠 주고, 끝나면 삭제한다")
st = [("1. 프로젝트", ["console.cloud.google.com", "새 프로젝트 만들기", "결제 계정 연결"], BLUE),
      ("2. API 사용 설정", ["API 및 서비스 →", "라이브러리 →", "Cloud Vision API 사용"], GREEN),
      ("3. API 키 만들기", ["사용자 인증 정보 →", "+ 사용자 인증 정보 만들기", "→ API 키"], ORANGE),
      ("4. 키 제한", ["API 제한: Cloud Vision API만", "할당량(요청/일) 제한", "예산 알림 설정"], PURPLE),
      ("5. 수업 후", ["키 삭제 또는 사용 중지", "공개 자료에 키 금지", "(Notion·GitHub·Drive)"], RED)]
for i, (h, b, c) in enumerate(st):
    x = 30 + i * 272
    s.box(x, 110, 250, 190, c, h, b)
    if i < 4:
        s.arrow(x + 252, 205, x + 270, 205)
s.rect(30, 330, 1340, 110, "#fafbfc", LINE)
s.text(60, 365, "학생 입력 위치: 워크북 2 Colab = getpass 입력창(노트북에 저장 안 됨) / 워크북 1 ESP32 = 시리얼 모니터 입력(전원 끄면 사라짐)",
       15, INK, "start")
s.text(60, 400, "비용: LABEL_DETECTION은 매월 처음 1,000건 무료, 이후 1,000건당 과금 → 80장 캐시를 강의자가 1회 만들어 두면 학생 호출을 크게 줄일 수 있다",
       15, INK, "start")
s.save("11_api_key_setup")
print("done")

# ---------------------------------------------------------------- 12 Wokwi 따라하기
s = Svg(1400, 560, "실물 보드가 없을 때 — Wokwi 시뮬레이터로 따라하기",
        "wokwi.com 에서 같은 회로를 불러와 예제 1~4를 실행한다 (회로 = diagram.json, 코드 = sketch.ino)")
st = [("1. 새 프로젝트", ["wokwi.com/projects/new/esp32", "(로그인하면 저장 가능)"], BLUE),
      ("2. 회로 붙여넣기", ["diagram.json 탭 전체 지우고", "강의 diagram.json 붙여넣기"], GREEN),
      ("3. 라이브러리", ["Library Manager → +", "ArduinoJson 추가 (예제3·4)"], ORANGE),
      ("4. 코드 붙여넣기", ["sketch.ino 탭에", "wokwi/exN_*.ino 붙여넣기"], PURPLE),
      ("5. ▶ 실행", ["빌드 대기 1~2분", "버튼은 0.5초 이상 꾹"], RED)]
for i, (h, b, c) in enumerate(st):
    x = 30 + i * 272
    s.box(x, 110, 250, 150, c, h, b)
    if i < 4:
        s.arrow(x + 252, 185, x + 270, 185)
s.rect(30, 290, 1340, 240, "#fafbfc", LINE)
s.text(60, 325, "실물 보드와 다른 점", 16, INK, "start", True)
rows = [("Wi-Fi", "SSID \"Wokwi-GUEST\", 비밀번호 없음, 채널 6 → Wokwi용 코드에 이미 설정됨"),
        ("인터넷", "GitHub 이미지 다운로드(예제2)는 가능 / 구글 Vision 서버와의 HTTPS는 끊김(2026-11 확인)"),
        ("Vision", "예제3·4 Wokwi판은 강의자가 저장한 vision_cache.json을 읽어 같은 매핑·정확도 계산 (API 키 불필요)"),
        ("속도", "시뮬레이션이 실제보다 느림(3~70%) → 버튼은 0.5초 이상 누르고, 결과를 기다린다"),
        ("소리", "부저 소리는 브라우저에서 재생 (PC 음소거 해제)")]
for i, (a, b) in enumerate(rows):
    s.text(60, 362 + i * 34, a, 15, BLUE, "start", True)
    s.text(150, 362 + i * 34, b, 15, INK, "start")
s.save("12_wokwi_steps")
print("done12")
