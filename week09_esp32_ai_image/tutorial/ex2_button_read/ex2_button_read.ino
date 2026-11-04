/*
  9주차 예제 2 — 버튼 4개 상태 읽기 (디지털 입력 + 내부 풀업)
  보드 : ESP32-DevKitC V4 ("ESP32 Dev Module")

  연결 (모든 버튼 공통, 저항 필요 없음)
    GPIO ── 택트 스위치 한쪽 다리
    택트 스위치 대각선 반대쪽 다리 ── GND

    BTN1 = GPIO23, BTN2 = GPIO22, BTN3 = GPIO21, BTN4 = GPIO19

  원리 : INPUT_PULLUP 으로 설정하면 ESP32 내부 저항(약 45kΩ)이 핀을 3.3V로 끌어올린다.
         → 버튼을 안 누르면 HIGH(1), 누르면 GND와 연결되어 LOW(0).
  동작 : 시리얼 모니터에 버튼 4개 상태가 "1 1 1 1" 형태로 0.2초마다 출력된다.
         누른 버튼만 0 으로 바뀌는지 확인한다.
*/

const int BTN_PINS[4] = {23, 22, 21, 19};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);     // 입력 + 내부 풀업 저항 사용
  }
  Serial.println("예제2: 버튼 상태 (1=안 누름, 0=누름)");
  Serial.println("BTN1 BTN2 BTN3 BTN4");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    int state = digitalRead(BTN_PINS[i]);   // HIGH(1) 또는 LOW(0)
    Serial.printf("  %d  ", state);
  }
  Serial.println();
  delay(200);
}

