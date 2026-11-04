/*
  9주차 예제 1 — LED 4개 차례로 켜기 (디지털 출력)
  보드 : ESP32-DevKitC V4 (Arduino IDE 보드 선택: "ESP32 Dev Module")

  연결 (모든 LED 공통)
    GPIO ── 220Ω 저항 ── LED 긴 다리(+, 애노드)
    LED 짧은 다리(-, 캐소드) ── GND

    LED1 = GPIO32, LED2 = GPIO33, LED3 = GPIO25, LED4 = GPIO26

  동작 : LED1 → LED2 → LED3 → LED4 순서로 0.3초씩 켜지고, 시리얼 모니터(115200)에 번호가 출력된다.
*/

const int LED_PINS[4] = {32, 33, 25, 26};   // LED 4개가 연결된 GPIO 번호

void setup() {
  Serial.begin(115200);                     // 시리얼 모니터 속도: 115200
  for (int i = 0; i < 4; i++) {
    pinMode(LED_PINS[i], OUTPUT);           // 핀을 '출력'으로 설정
    digitalWrite(LED_PINS[i], LOW);         // 처음에는 모두 끔
  }
  Serial.println("예제1: LED 차례로 켜기 시작");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_PINS[i], HIGH);        // 3.3V 출력 → LED 켜짐
    Serial.printf("LED%d ON (GPIO%d)\n", i + 1, LED_PINS[i]);
    delay(300);                             // 0.3초 기다림
    digitalWrite(LED_PINS[i], LOW);         // 0V 출력 → LED 꺼짐
  }
}

