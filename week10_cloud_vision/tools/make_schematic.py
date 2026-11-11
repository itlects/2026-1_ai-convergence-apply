"""9주차 회로도 SVG의 글자를 10주차 용도로 바꾼다 (배선은 동일)."""
from pathlib import Path
import sys
s = Path(sys.argv[1]).read_text(encoding="utf-8")
pairs = [
    (">실습 전체 회로도 (Schematic)<", ">10주차 회로도 (Schematic) — 9주차와 같은 배선<"),
    (">LED·부저 = 출력 3채널+1, 버튼 = 입력 4채널 · 모든 GND 공통<",
     ">LED = 예측 클래스 표시, 버튼 = 분류 실행, 부저 = 정답/오답 · 모든 GND 공통<"),
    (">LED1<", ">LED1 apple<"), (">LED2<", ">LED2 banana<"),
    (">LED3<", ">LED3 orange<"), (">LED4<", ">LED4 lemon<"),
    (">BTN1<", ">BTN1 다음<"), (">BTN2<", ">BTN2 전체<"),
    (">BTN3<", ">BTN3 (미사용)<"), (">BTN4<", ">BTN4 (미사용)<"),
    (">코드와 연결<", ">10주차 코드와 연결<"),
    (">출력: pinMode(pin, OUTPUT) + digitalWrite()<", ">showClass(i): LED i 하나만 HIGH, unknown은 4개 깜빡임<"),
    (">입력: pinMode(pin, INPUT_PULLUP) + digitalRead()<", ">BTN1 → classifyOne(), BTN2 → evaluateAll()<"),
    (">부저: tone(27, Hz, ms)<", ">부저: 정답 tone(27,1047) / 오답 tone(27,262) x2<"),
]
for a, b in pairs:
    assert a in s, a
    s = s.replace(a, b, 1)
Path(sys.argv[2]).write_text(s, encoding="utf-8")
