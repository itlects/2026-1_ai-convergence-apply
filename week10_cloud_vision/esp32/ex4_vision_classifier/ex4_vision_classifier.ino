/*
  10주차 예제 4 (종합) — Cloud Vision 라벨 → 4개 과일 클래스 분류 → LED·부저 표시 → 정확도
  보드 : ESP32-DevKitC V4  ("ESP32 Dev Module")
  회로 : 예제1과 같음 (그림: diagrams/03_wiring_devkitc.png)
           LED1 32=apple  LED2 33=banana  LED3 25=orange  LED4 26=lemon
           BTN1 23=[다음] 1장 분류   BTN2 22=[전체] 시험 데이터 12장 평가   BUZZER 27
  라이브러리 : ArduinoJson 7.x

  핵심 아이디어 (그림: diagrams/06_label_mapping.png)
    Cloud Vision은 "Fruit", "Citrus", "Lemon" 처럼 자유로운 라벨 여러 개를 준다.
    우리가 원하는 것은 4개 중 하나(apple/banana/orange/lemon)이므로
    '매핑 규칙'(키워드 표 + 최소 점수)을 만들어 라벨 → 클래스로 바꾼다.
      - score >= MIN_SCORE 인 라벨 중에서
      - 클래스 키워드가 들어 있는 라벨의 score가 가장 높은 클래스를 예측으로 고른다.
      - 하나도 없으면 "unknown" (= 오답으로 계산)
    ※ 이 규칙(키워드, MIN_SCORE)은 워크북 2에서 '검증(val) 데이터'로 정한 값을 그대로 옮긴다.
      시험(test) 데이터를 보고 규칙을 고치면 안 된다!

  출력
    BTN1 : 시험 이미지 1장 → 예측 LED 점등, 정답이면 '삑', 오답이면 '삑-삑', unknown이면 LED 4개 깜빡임
    BTN2 : 시험 이미지 12장 전체 → 이미지별 결과 표 + 정확도 + 혼동행렬
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <base64.h>
#include <ArduinoJson.h>

// ======== 학생 수정 구간 ========
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// 워크북 2(검증 데이터)에서 결정한 매핑 규칙을 옮겨 적는다
const float MIN_SCORE = 0.50;
const char* KEYWORDS[4][5] = {
  {"apple", "mcintosh", "malus", nullptr, nullptr},          // 0 apple
  {"banana", "plantain", nullptr, nullptr, nullptr},         // 1 banana
  {"orange", "tangerine", "mandarin", "clementine", nullptr},// 2 orange
  {"lemon", "citron", nullptr, nullptr, nullptr}             // 3 lemon
};
// ===============================

const char* CLASS_NAMES[5] = {"apple", "banana", "orange", "lemon", "unknown"};
const int UNKNOWN = 4;

const char* IMAGE_BASE =
  "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
  "main/week10_cloud_vision/dataset/week10_fruits/";
const char* VISION_URL = "https://vision.googleapis.com/v1/images:annotate?key=";

// 워크북 2와 같은 분할(random seed 42)의 시험(test) 데이터 12장과 정답
struct Sample {
  const char* path;
  int label;
};
const Sample TEST_SET[] = {
  {"images/apple/apple_09.jpg", 0},
  {"images/apple/apple_01.jpg", 0},
  {"images/apple/apple_04.jpg", 0},
  {"images/banana/banana_20.jpg", 1},
  {"images/banana/banana_07.jpg", 1},
  {"images/banana/banana_18.jpg", 1},
  {"images/lemon/lemon_19.jpg", 3},
  {"images/lemon/lemon_12.jpg", 3},
  {"images/lemon/lemon_04.jpg", 3},
  {"images/orange/orange_08.jpg", 2},
  {"images/orange/orange_02.jpg", 2},
  {"images/orange/orange_03.jpg", 2},
};
const int N_TEST = sizeof(TEST_SET) / sizeof(TEST_SET[0]);

const int LED_PINS[4] = {32, 33, 25, 26};
const int BTN_NEXT = 23;
const int BTN_ALL = 22;
const int BUZZER_PIN = 27;
const int MAX_LABELS = 10;
const size_t MAX_IMAGE_BYTES = 32 * 1024;

uint8_t imageBuf[MAX_IMAGE_BYTES];
String apiKey;
int nextIndex = 0;

// ================= 표시(LED·부저) =================
void showClass(int idx) {
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_PINS[i], i == idx ? HIGH : LOW);
  }
}

void blinkUnknown() {
  for (int k = 0; k < 3; k++) {
    for (int i = 0; i < 4; i++) digitalWrite(LED_PINS[i], HIGH);
    delay(150);
    for (int i = 0; i < 4; i++) digitalWrite(LED_PINS[i], LOW);
    delay(150);
  }
}

void beepCorrect() {
  tone(BUZZER_PIN, 1047, 120);
}

void beepWrong() {
  tone(BUZZER_PIN, 262, 120);
  delay(180);
  tone(BUZZER_PIN, 262, 120);
}

// ================= Wi-Fi / 키 =================
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
  Serial.println(">> Cloud Vision API 키를 붙여넣고 Enter (줄 끝: 새 줄)");
  apiKey = readLineFromSerial();
  apiKey.trim();
  Serial.printf("키 입력 완료: %s****** (%u글자)\n",
                apiKey.substring(0, 6).c_str(), apiKey.length());
}

// ================= 다운로드 / Vision (예제 2·3과 같음) =================
int downloadFile(const String& url, uint8_t* buf, size_t maxLen) {
  WiFiClientSecure client;
  client.setInsecure();
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
  http.setConnectTimeout(20000);               // 시뮬레이터(Wokwi)는 느리므로 넉넉하게
  http.setTimeout(20000);
  if (!http.begin(client, String(VISION_URL) + apiKey)) return -1;
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(body);
  if (code < 0) {                              // 서버에 연결하지 못함 (Wi-Fi, DNS, TLS, 시간 초과)
    Serial.printf("[연결 오류] %d: %s\n", code, http.errorToString(code).c_str());
    http.end();
    return -1;
  }
  String resp = http.getString();
  http.end();

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

  int n = 0;
  for (JsonObject item : doc["responses"][0]["labelAnnotations"].as<JsonArray>()) {
    if (n >= maxLabels) break;
    labels[n] = item["description"].as<String>();
    scores[n] = item["score"].as<float>();
    n++;
  }
  return n;
}

// ================= 매핑 규칙: 라벨 목록 → 클래스 번호 =================
int mapToClass(String labels[], float scores[], int n, float& bestScore, String& matched) {
  int best = UNKNOWN;
  bestScore = 0.0;
  matched = "-";

  for (int i = 0; i < n; i++) {
    if (scores[i] < MIN_SCORE) continue;
    String desc = labels[i];
    desc.toLowerCase();

    for (int c = 0; c < 4; c++) {
      for (int k = 0; k < 5 && KEYWORDS[c][k] != nullptr; k++) {
        if (desc.indexOf(KEYWORDS[c][k]) >= 0 && scores[i] > bestScore) {
          best = c;
          bestScore = scores[i];
          matched = labels[i];
        }
      }
    }
  }
  return best;
}

// 1장 분류: 예측 번호를 돌려준다 (통신 오류: -1)
int classifyOne(int idx, bool verbose) {
  const Sample& s = TEST_SET[idx];
  int len = downloadFile(String(IMAGE_BASE) + s.path, imageBuf, MAX_IMAGE_BYTES);
  if (len <= 0) return -1;

  String labels[MAX_LABELS];
  float scores[MAX_LABELS];
  int n = callVision(imageBuf, len, labels, scores, MAX_LABELS);
  if (n < 0) return -1;

  float bestScore;
  String matched;
  int pred = mapToClass(labels, scores, n, bestScore, matched);

  if (verbose) {
    Serial.println("  Vision 라벨:");
    for (int i = 0; i < n; i++) {
      Serial.printf("    %-24s %.3f\n", labels[i].c_str(), scores[i]);
    }
  }
  Serial.printf("[%2d] %-28s 정답=%-7s 예측=%-7s 근거=%s(%.2f) %s\n",
                idx + 1, s.path, CLASS_NAMES[s.label], CLASS_NAMES[pred],
                matched.c_str(), bestScore, pred == s.label ? "O" : "X");
  return pred;
}

void showResult(int pred, int truth) {
  if (pred == UNKNOWN) {
    blinkUnknown();
  } else {
    showClass(pred);
  }
  if (pred == truth) {
    beepCorrect();
  } else {
    beepWrong();
  }
}

// ================= BTN2: 시험 데이터 전체 평가 =================
void evaluateAll() {
  int cm[4][5] = {0};      // 행: 정답 4개, 열: 예측 4개 + unknown
  int correct = 0;
  int done = 0;

  Serial.println();
  Serial.printf("===== 시험(test) 데이터 %d장 평가 (MIN_SCORE=%.2f) =====\n", N_TEST, MIN_SCORE);
  for (int i = 0; i < N_TEST; i++) {
    showClass(i % 4);                         // 진행 중 표시
    int pred = classifyOne(i, false);
    if (pred < 0) {
      Serial.println("  → 통신 오류로 이 이미지는 제외");
      continue;
    }
    cm[TEST_SET[i].label][pred]++;
    if (pred == TEST_SET[i].label) correct++;
    done++;
  }

  if (done == 0) {
    Serial.println("평가된 이미지가 없습니다.");
    return;
  }

  float acc = (float)correct / done;
  Serial.printf("\n정확도(Accuracy) = %d / %d = %.3f\n", correct, done, acc);
  Serial.println("\n혼동행렬 (행=정답, 열=예측)");
  Serial.println("            apple banana orange  lemon unknown");
  for (int r = 0; r < 4; r++) {
    Serial.printf("  %-8s", CLASS_NAMES[r]);
    for (int c = 0; c < 5; c++) {
      Serial.printf("%7d", cm[r][c]);
    }
    Serial.println();
  }

  showClass(-1);
  if (acc >= 0.75) {
    beepCorrect();
  } else {
    beepWrong();
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);
  for (int i = 0; i < 4; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  pinMode(BTN_NEXT, INPUT_PULLUP);
  pinMode(BTN_ALL, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);

  Serial.println();
  Serial.println("=== 10주차 예제4: Vision 라벨 → 과일 4종 분류기 ===");
  connectWiFi();
  askApiKey();
  Serial.println("BTN1(GPIO23)=시험 이미지 1장 분류, BTN2(GPIO22)=시험 데이터 12장 전체 평가");
}

void loop() {
  static int lastNext = HIGH;
  static int lastAll = HIGH;
  int bNext = digitalRead(BTN_NEXT);
  int bAll = digitalRead(BTN_ALL);

  if (lastNext == HIGH && bNext == LOW) {
    delay(30);
    if (digitalRead(BTN_NEXT) == LOW) {
      if (WiFi.status() != WL_CONNECTED) connectWiFi();
      Serial.println();
      int pred = classifyOne(nextIndex, true);
      if (pred >= 0) showResult(pred, TEST_SET[nextIndex].label);
      nextIndex = (nextIndex + 1) % N_TEST;
    }
  }

  if (lastAll == HIGH && bAll == LOW) {
    delay(30);
    if (digitalRead(BTN_ALL) == LOW) {
      if (WiFi.status() != WL_CONNECTED) connectWiFi();
      evaluateAll();
    }
  }

  lastNext = bNext;
  lastAll = bAll;
}
