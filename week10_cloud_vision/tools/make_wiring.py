"""9주차 연결도 SVG를 바탕으로 10주차(분류 결과 표시) 연결도를 만든다."""
from pathlib import Path
import re, sys
src = Path(sys.argv[1]).read_text(encoding="utf-8")
out = Path(sys.argv[2])

def rep(old, new):
    global src
    assert old in src, old
    src = src.replace(old, new, 1)

rep(">실습 전체 연결도 — 버튼 4 · LED 4 · 부저 (ESP32-DevKitC V4)<",
    ">10주차 연결도 — 9주차 회로 그대로 · LED = 분류 결과, 버튼 = 실행 (ESP32-DevKitC V4)<")
rep(">왼쪽 핀열 → LED·부저 / 오른쪽 핀열 → 버튼 · 모든 부품의 (−) 쪽은 GND 레일(파란 줄)로 모은다<",
    ">LED1~4 = apple·banana·orange·lemon 예측 표시 / BTN1 = 다음 1장, BTN2 = 시험 12장 전체 / 부저 = 정답·오답 소리<")

def add(x, y, text, color="#1d2433", size=13, anchor="middle", weight="bold"):
    global src
    src = src.replace("</svg>",
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
        f'font-weight="{weight}">{text}</text></svg>')

for y, name, color in [(180, "→ apple (사과)", "#c62828"), (310, "→ banana (바나나)", "#9a7400"),
                       (560, "→ orange (오렌지)", "#2e7d32"), (690, "→ lemon (레몬)", "#1565c0")]:
    add(280, y, name, color, 14)
add(260, 920, "정답 '삑' / 오답 '삑-삑'", "#e08a1e", 12, weight="normal")
add(1254, 386, "[다음] 시험 이미지 1장 분류", "#2f6fd6", 12)
add(1254, 536, "[전체] 시험 12장 평가·정확도", "#2f6fd6", 12)
add(1254, 686, "(10주차 미사용)", "#9aa3b2", 12, weight="normal")
add(1254, 836, "(10주차 미사용)", "#9aa3b2", 12, weight="normal")
rep('<rect x="960" y="930" width="510" height="112"', '<rect x="960" y="930" width="510" height="134"')
add(976, 1048, "수동 피에조 · 원하면 100Ω 보호저항 직렬 추가", size=14, anchor="start", weight="normal")
out.write_text(src, encoding="utf-8")
