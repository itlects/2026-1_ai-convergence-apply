"""9주차 Wokwi 회로(diagram.json)를 10주차용 라벨로 바꾸고, 예제 1~4의 Wokwi용 스케치를 만든다.

python3 tools/make_wokwi.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "week09_esp32_ai_image/tutorial/wokwi/diagram.json"
OUT = ROOT / "wokwi"
OUT.mkdir(exist_ok=True)

d = json.loads(SRC.read_text(encoding="utf-8"))
labels = {
    "led0": ("red", "LED1 apple GPIO32"),
    "led1": ("yellow", "LED2 banana GPIO33"),
    "led2": ("orange", "LED3 orange GPIO25"),
    "led3": ("green", "LED4 lemon GPIO26"),
    "btn0": ("green", "BTN1 next GPIO23"),
    "btn1": ("blue", "BTN2 all GPIO22"),
    "btn2": ("white", "B3 unused GPIO21"),
    "btn3": ("white", "B4 unused GPIO19"),
}
for p in d["parts"]:
    if p["id"] in labels:
        p["attrs"]["color"], p["attrs"]["label"] = labels[p["id"]]
d["serialMonitor"] = {"display": "always", "newline": "lf"}
(OUT / "diagram.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "libraries.txt").write_text("# Wokwi Library Manager\nArduinoJson\n", encoding="utf-8")

NOTE = (
    "/*\n  [Wokwi 시뮬레이터용] 실물 보드 코드와 같고 Wi-Fi만 Wokwi 가상 공유기로 바꿨다.\n"
    "  - SSID \"Wokwi-GUEST\", 비밀번호 없음 (Wokwi가 인터넷에 연결해 준다)\n"
    "  - 회로: wokwi/diagram.json, 라이브러리: wokwi/libraries.txt (ArduinoJson)\n*/\n"
)
for ex in ["ex1_circuit_check", "ex2_wifi_https_image", "ex3_vision_labels", "ex4_vision_classifier"]:
    src = (ROOT / "esp32" / ex / f"{ex}.ino").read_text(encoding="utf-8")
    if "WIFI_SSID" in src:
        src = src.replace('const char* WIFI_SSID = "YOUR_WIFI_SSID";', 'const char* WIFI_SSID = "Wokwi-GUEST";')
        src = src.replace('const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";', 'const char* WIFI_PASSWORD = "";')
        assert "Wokwi-GUEST" in src
        src = NOTE + src
    (OUT / f"{ex}.ino").write_text(src, encoding="utf-8")
print(sorted(p.name for p in OUT.iterdir()))
