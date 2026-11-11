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
CACHE_BLOCK = r'''
// ======== Wokwi 전용: 캐시 모드 ========
// Wokwi 가상 Wi-Fi에서는 구글 서버(vision.googleapis.com)와의 HTTPS 연결이 끊긴다(2026-11 확인).
// 그래서 Vision을 직접 부르는 대신, 강의자가 같은 80장을 Vision으로 미리 분석해 저장한
// vision_cache.json 에서 해당 이미지의 라벨을 읽는다. JSON 해석·매핑·정확도 계산은 실물 보드와 같다.
// 실물 보드에서는 USE_CACHE = false 로 바꾸면 실제 Vision API를 호출한다.
const bool USE_CACHE = true;
const char* CACHE_URL =
  "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
  "main/week10_cloud_vision/dataset/vision_cache.json";

int cacheLabels(const char* path, String labels[], float scores[], int maxLabels) {
  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;
  http.setConnectTimeout(20000);
  http.setTimeout(20000);
  if (!http.begin(client, CACHE_URL)) return -1;
  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    Serial.printf("[캐시 오류] HTTP %d - 강의자가 vision_cache.json 을 아직 올리지 않았을 수 있음\n", code);
    http.end();
    return -1;
  }

  JsonDocument filter;                       // 이 이미지의 라벨만 남긴다
  filter["labels"][path] = true;
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, http.getStream(), DeserializationOption::Filter(filter));
  http.end();
  if (err) {
    Serial.printf("[캐시 JSON 오류] %s\n", err.c_str());
    return -1;
  }

  int n = 0;
  for (JsonObject item : doc["labels"][path].as<JsonArray>()) {
    if (n >= maxLabels) break;
    labels[n] = item["description"].as<String>();
    scores[n] = item["score"].as<float>();
    n++;
  }
  return n;
}
// ======================================
'''

for ex in ["ex1_circuit_check", "ex2_wifi_https_image", "ex3_vision_labels", "ex4_vision_classifier"]:
    src = (ROOT / "esp32" / ex / f"{ex}.ino").read_text(encoding="utf-8")
    if "WIFI_SSID" in src:
        src = src.replace('const char* WIFI_SSID = "YOUR_WIFI_SSID";', 'const char* WIFI_SSID = "Wokwi-GUEST";')
        src = src.replace('const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";', 'const char* WIFI_PASSWORD = "";')
        assert "Wokwi-GUEST" in src
        src = NOTE + src
        n = src.count("WiFi.begin(WIFI_SSID, WIFI_PASSWORD);")
        assert n == 1, ex
        src = src.replace("WiFi.begin(WIFI_SSID, WIFI_PASSWORD);",
                          "WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);   // Wokwi-GUEST는 6번 채널 (연결이 빨라짐)")
        src = src.replace("millis() - start > 20000", "millis() - start > 40000")
        src = src.replace("millis() - start < 20000", "millis() - start < 40000")
    if ex in ("ex3_vision_labels", "ex4_vision_classifier"):
        anchor = "// ---------------- ①" if ex == "ex3_vision_labels" else "// ================= 표시(LED·부저)"
        assert anchor in src, ex
        src = src.replace(anchor, CACHE_BLOCK.strip() + "\n\n" + anchor, 1)
        if ex == "ex3_vision_labels":
            old = "int n = callVision(imageBuf, len, labels, scores, MAX_LABELS);"
            new = ("int n = USE_CACHE ? cacheLabels(IMAGE_PATHS[idx], labels, scores, MAX_LABELS)\n"
                   "                    : callVision(imageBuf, len, labels, scores, MAX_LABELS);")
        else:
            old = "int n = callVision(imageBuf, len, labels, scores, MAX_LABELS);"
            new = ("int n = USE_CACHE ? cacheLabels(s.path, labels, scores, MAX_LABELS)\n"
                   "                    : callVision(imageBuf, len, labels, scores, MAX_LABELS);")
        assert src.count(old) == 1, ex
        src = src.replace(old, new)
        old = "  askApiKey();\n"
        assert src.count(old) == 1, ex
        src = src.replace(old, "  if (USE_CACHE) {\n    Serial.println(\"[Wokwi 캐시 모드] vision_cache.json 사용 (API 키 입력 없음)\");\n  } else {\n    askApiKey();\n  }\n")
    (OUT / f"{ex}.ino").write_text(src, encoding="utf-8")
print(sorted(p.name for p in OUT.iterdir()))
