/*
  10주차 예제 3 — ESP32에서 Cloud Vision API 직접 호출 (LABEL_DETECTION)
  보드 : ESP32-DevKitC V4  ("ESP32 Dev Module")
  회로 : 예제1과 같음 (LED1 GPIO32 = 통신 중 표시)
  라이브러리 : ArduinoJson (Benoit Blanchon) 7.x  ← 라이브러리 매니저에서 설치

  흐름 (그림: diagrams/05_esp32_vision_flow.png)
    ① HTTPS GET  : GitHub의 과일 이미지(JPEG) 다운로드
    ② Base64     : 바이트 → 문자열 변환
    ③ HTTPS POST : vision.googleapis.com/v1/images:annotate?key=API키
                   {"requests":[{"image":{"content":"Base64..."},
                                 "features":[{"type":"LABEL_DETECTION","maxResults":5}]}]}
    ④ JSON 해석  : responses[0].labelAnnotations[i].description / .score
    ⑤ 시리얼 출력: 라벨 이름과 신뢰도(score)

  API 키 입력
    - 키는 코드에 적지 않는다! 부팅 후 시리얼 모니터 입력창에 붙여넣고 Enter.
      (시리얼 모니터 오른쪽 아래 줄 끝 설정을 "새 줄(Newline)"로 맞출 것)
    - 강의자가 수업 시간에 나눠 준 키를 사용한다. 키는 보드를 껐다 켜면 사라진다.

  동작
    부팅 → Wi-Fi 연결 → API 키 입력 → 첫 이미지 분석
    BTN1(GPIO23)을 누를 때마다 다음 이미지(사과→바나나→오렌지→레몬)를 분석한다.
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <base64.h>
#include <ArduinoJson.h>

// ======== 학생 수정 구간 ========
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
// ===============================

const char* IMAGE_BASE =
  "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
  "main/week10_cloud_vision/dataset/week10_fruits/";
const char* VISION_URL = "https://vision.googleapis.com/v1/images:annotate?key=";

const char* IMAGE_PATHS[4] = {
  "images/apple/apple_02.jpg",     // 4장 모두 학습(train) 데이터
  "images/banana/banana_01.jpg",
  "images/orange/orange_01.jpg",
  "images/lemon/lemon_01.jpg"
};

const int LED_BUSY = 32;
const int BTN_NEXT = 23;
const int MAX_LABELS = 5;
const size_t MAX_IMAGE_BYTES = 32 * 1024;

uint8_t imageBuf[MAX_IMAGE_BYTES];
String apiKey;
int imageIndex = 0;

// ---------------- Wi-Fi ----------------
void connectWiFi() {
  Serial.printf("Wi-Fi 연결 중: %s ", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("[연결됨] IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("[실패] SSID/비밀번호, 2.4GHz 여부를 확인하세요");
  }
}

// ---------------- API 키 입력 ----------------
String readLineFromSerial() {
  String line = "";
  while (true) {
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n' || c == '\r') {
        if (line.length() > 0) return line;
      } else {
        line += c;
      }
    }
    delay(10);
  }
}

void askApiKey() {
  Serial.println();
  Serial.println(">> Cloud Vision API 키를 붙여넣고 Enter 를 누르세요 (줄 끝: 새 줄)");
  apiKey = readLineFromSerial();
  apiKey.trim();
  Serial.printf("키 입력 완료: %s****** (%u글자)\n",
                apiKey.substring(0, 6).c_str(), apiKey.length());
}

// ---------------- ① 이미지 다운로드 ----------------
int downloadFile(const String& url, uint8_t* buf, size_t maxLen) {
  WiFiClientSecure client;
  client.setInsecure();   // 수업용: 인증서 검증 생략
  HTTPClient http;
  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  if (!http.begin(client, url)) return -1;

  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    Serial.printf("[다운로드 오류] HTTP %d\n", code);
    http.end();
    return -1;
  }

  int total = http.getSize();
  WiFiClient* stream = http.getStreamPtr();
  size_t received = 0;
  unsigned long lastData = millis();
  while (http.connected() && (total < 0 || (int)received < total)) {
    size_t avail = stream->available();
    if (avail) {
      if (received + avail > maxLen) {
        http.end();
        return -1;
      }
      received += stream->readBytes(buf + received, avail);
      lastData = millis();
    } else if (millis() - lastData > 5000) {
      break;
    } else {
      delay(1);
    }
  }
  http.end();
  return (int)received;
}

// ---------------- ②③④ Vision 호출 ----------------
// labels[], scores[] 에 결과를 채우고 라벨 개수를 돌려준다 (오류: -1)
int callVision(const uint8_t* img, int len, String labels[], float scores[], int maxLabels) {
  String body;
  body.reserve(len * 4 / 3 + 200);
  body += "{\"requests\":[{\"image\":{\"content\":\"";
  body += base64::encode(img, len);
  body += "\"},\"features\":[{\"type\":\"LABEL_DETECTION\",\"maxResults\":";
  body += String(maxLabels);
  body += "}]}]}";

  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;
  http.setTimeout(15000);
  if (!http.begin(client, String(VISION_URL) + apiKey)) return -1;
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(body);
  String resp = http.getString();
  http.end();

  // 필요한 값만 남기는 필터 → 메모리 절약
  JsonDocument filter;
  filter["responses"][0]["labelAnnotations"][0]["description"] = true;
  filter["responses"][0]["labelAnnotations"][0]["score"] = true;
  filter["responses"][0]["error"]["message"] = true;
  filter["error"]["message"] = true;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, resp, DeserializationOption::Filter(filter));
  if (err) {
    Serial.printf("[JSON 오류] %s (HTTP %d)\n", err.c_str(), code);
    return -1;
  }

  if (code != HTTP_CODE_OK || !doc["error"]["message"].isNull()) {
    Serial.printf("[API 오류] HTTP %d: %s\n", code, doc["error"]["message"] | "(메시지 없음)");
    return -1;
  }
  if (!doc["responses"][0]["error"]["message"].isNull()) {
    Serial.printf("[API 오류] %s\n", doc["responses"][0]["error"]["message"].as<const char*>());
    return -1;
  }

  JsonArray arr = doc["responses"][0]["labelAnnotations"].as<JsonArray>();
  int n = 0;
  for (JsonObject item : arr) {
    if (n >= maxLabels) break;
    labels[n] = item["description"].as<String>();
    scores[n] = item["score"].as<float>();
    n++;
  }
  return n;
}

// ---------------- ⑤ 한 장 분석 ----------------
void analyze(int idx) {
  Serial.println();
  Serial.printf("[%d/4] %s\n", idx + 1, IMAGE_PATHS[idx]);
  digitalWrite(LED_BUSY, HIGH);

  unsigned long t0 = millis();
  int len = downloadFile(String(IMAGE_BASE) + IMAGE_PATHS[idx], imageBuf, MAX_IMAGE_BYTES);
  if (len <= 0) {
    digitalWrite(LED_BUSY, LOW);
    return;
  }

  String labels[MAX_LABELS];
  float scores[MAX_LABELS];
  int n = callVision(imageBuf, len, labels, scores, MAX_LABELS);
  unsigned long t1 = millis();
  digitalWrite(LED_BUSY, LOW);

  if (n < 0) return;
  Serial.printf("  이미지 %d bytes, 처리 시간 %lu ms\n", len, t1 - t0);
  Serial.println("  순위  label.description          label.score");
  for (int i = 0; i < n; i++) {
    Serial.printf("  %2d    %-26s %.3f\n", i + 1, labels[i].c_str(), scores[i]);
  }
  if (n == 0) Serial.println("  (라벨 없음)");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(LED_BUSY, OUTPUT);
  pinMode(BTN_NEXT, INPUT_PULLUP);

  Serial.println();
  Serial.println("=== 10주차 예제3: ESP32 → Cloud Vision 라벨 검출 ===");
  connectWiFi();
  askApiKey();
  analyze(imageIndex);
  Serial.println("\nBTN1(GPIO23)을 누르면 다음 이미지를 분석합니다.");
}

void loop() {
  static int lastBtn = HIGH;
  int btn = digitalRead(BTN_NEXT);
  if (lastBtn == HIGH && btn == LOW) {
    delay(30);
    if (digitalRead(BTN_NEXT) == LOW) {
      if (WiFi.status() != WL_CONNECTED) connectWiFi();
      imageIndex = (imageIndex + 1) % 4;
      analyze(imageIndex);
    }
  }
  lastBtn = btn;
}
