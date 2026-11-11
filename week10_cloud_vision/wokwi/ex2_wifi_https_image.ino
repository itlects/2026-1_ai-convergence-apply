/*
  [Wokwi 시뮬레이터용] 실물 보드 코드와 같고 Wi-Fi만 Wokwi 가상 공유기로 바꿨다.
  - SSID "Wokwi-GUEST", 비밀번호 없음 (Wokwi가 인터넷에 연결해 준다)
  - 회로: wokwi/diagram.json, 라이브러리: wokwi/libraries.txt (ArduinoJson)
*/
/*
  10주차 예제 2 — Wi-Fi 연결 + HTTPS로 이미지(JPEG) 내려받기 + Base64 변환
  보드 : ESP32-DevKitC V4  ("ESP32 Dev Module")
  회로 : 예제1과 같음 (LED1 GPIO32는 '다운로드 중' 표시로 사용)

  왜 필요한가?
    DevKitC V4에는 카메라가 없다. 그래서 9주차처럼 직접 찍는 대신
    GitHub에 올려 둔 실습 이미지(100x100 JPEG)를 인터넷으로 받아 온다.
    Cloud Vision API는 이미지를 'Base64 문자열'로 받기 때문에 변환까지 해 본다.

  준비
    - 아래 WIFI_SSID / WIFI_PASSWORD 를 수정한다. (ESP32는 2.4GHz Wi-Fi만 연결 가능)
    - 학교 인증형 Wi-Fi(아이디+비밀번호 로그인)는 안 되므로 휴대폰 핫스팟(2.4GHz)을 권장한다.

  동작
    부팅 → Wi-Fi 연결(IP, 신호세기 출력) → 첫 번째 이미지 다운로드
    BTN1(GPIO23)을 누를 때마다 다음 이미지를 내려받아
    크기(byte), JPEG 시작 표식(FF D8 FF), Base64 길이를 출력한다.
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <base64.h>

// ======== 학생 수정 구간 ========
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";
// ===============================

const char* IMAGE_BASE =
  "https://raw.githubusercontent.com/itlects/2026-1_ai-convergence-apply/"
  "main/week10_cloud_vision/dataset/week10_fruits/";

const char* IMAGE_PATHS[4] = {
  "images/apple/apple_02.jpg",     // 4장 모두 학습(train) 데이터
  "images/banana/banana_01.jpg",
  "images/orange/orange_01.jpg",
  "images/lemon/lemon_01.jpg"
};

const int LED_BUSY = 32;
const int BTN_NEXT = 23;
const size_t MAX_IMAGE_BYTES = 32 * 1024;   // 실습 이미지는 약 2~6KB

uint8_t imageBuf[MAX_IMAGE_BYTES];
int imageIndex = 0;

void connectWiFi() {
  Serial.printf("Wi-Fi 연결 중: %s ", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - start > 20000) {
      Serial.println("\n[실패] 20초 안에 연결되지 않음 → SSID/비밀번호, 2.4GHz 여부 확인");
      return;
    }
  }
  Serial.println();
  Serial.print("[연결됨] IP 주소: ");
  Serial.println(WiFi.localIP());
  Serial.printf("신호 세기(RSSI): %d dBm  (-70보다 크면 양호)\n", WiFi.RSSI());
}

// HTTPS GET 으로 파일을 buf 에 저장하고, 받은 바이트 수를 돌려준다 (실패 시 -1)
int downloadFile(const String& url, uint8_t* buf, size_t maxLen) {
  WiFiClientSecure client;
  client.setInsecure();   // 수업용: 인증서 검증 생략 (실제 제품은 루트 인증서로 검증해야 함)

  HTTPClient http;
  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  if (!http.begin(client, url)) {
    Serial.println("[오류] http.begin 실패");
    return -1;
  }

  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    Serial.printf("[오류] HTTP 상태 코드 %d\n", code);
    http.end();
    return -1;
  }

  int total = http.getSize();               // 서버가 알려준 크기 (모르면 -1)
  WiFiClient* stream = http.getStreamPtr();
  size_t received = 0;
  unsigned long lastData = millis();

  while (http.connected() && (total < 0 || (int)received < total)) {
    size_t avail = stream->available();
    if (avail) {
      if (received + avail > maxLen) {
        Serial.println("[오류] 버퍼보다 큰 파일");
        http.end();
        return -1;
      }
      received += stream->readBytes(buf + received, avail);
      lastData = millis();
    } else if (millis() - lastData > 5000) {
      break;                                 // 5초 동안 데이터가 없으면 종료
    } else {
      delay(1);
    }
  }
  http.end();
  return (int)received;
}

void downloadAndShow(int idx) {
  String url = String(IMAGE_BASE) + IMAGE_PATHS[idx];
  Serial.println();
  Serial.printf("[%d/4] 다운로드: %s\n", idx + 1, IMAGE_PATHS[idx]);

  digitalWrite(LED_BUSY, HIGH);
  unsigned long t0 = millis();
  int n = downloadFile(url, imageBuf, MAX_IMAGE_BYTES);
  unsigned long t1 = millis();
  digitalWrite(LED_BUSY, LOW);

  if (n <= 0) return;

  Serial.printf("  크기: %d bytes, 걸린 시간: %lu ms\n", n, t1 - t0);
  Serial.printf("  첫 3바이트: %02X %02X %02X  (FF D8 FF 이면 JPEG)\n",
                imageBuf[0], imageBuf[1], imageBuf[2]);

  String b64 = base64::encode(imageBuf, n);
  Serial.printf("  Base64 길이: %u 글자 (원본의 약 4/3배)\n", b64.length());
  Serial.print("  Base64 앞부분: ");
  Serial.println(b64.substring(0, 40) + "...");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(LED_BUSY, OUTPUT);
  pinMode(BTN_NEXT, INPUT_PULLUP);

  Serial.println();
  Serial.println("=== 10주차 예제2: Wi-Fi + HTTPS 이미지 다운로드 ===");
  connectWiFi();
  if (WiFi.status() == WL_CONNECTED) {
    downloadAndShow(imageIndex);
  }
  Serial.println("\nBTN1(GPIO23)을 누르면 다음 이미지를 받습니다.");
}

void loop() {
  static int lastBtn = HIGH;
  int btn = digitalRead(BTN_NEXT);

  if (lastBtn == HIGH && btn == LOW) {        // 누르는 순간
    delay(30);                                // 간단한 채터링 방지
    if (digitalRead(BTN_NEXT) == LOW) {
      if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
      }
      imageIndex = (imageIndex + 1) % 4;
      downloadAndShow(imageIndex);
    }
  }
  lastBtn = btn;
}
