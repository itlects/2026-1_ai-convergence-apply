/*
  9주차 예제 3 — 버튼을 누르는 동안 LED 켜기 (입력 → 출력)
  보드 : ESP32-DevKitC V4 ("ESP32 Dev Module")

  연결 : 예제1의 LED 4개 + 예제2의 버튼 4개를 함께 연결한 상태
    BTN1(GPIO23) → LED1(GPIO32)
    BTN2(GPIO22) → LED2(GPIO33)
    BTN3(GPIO21) → LED3(GPIO25)
    BTN4(GPIO19) → LED4(GPIO26)

  동작 : 버튼을 누르고 있는 동안만 같은 번호의 LED가 켜진다.
*/

const int BTN_PINS[4] = {23, 22, 21, 19};
const int LED_PINS[4] = {32, 33, 25, 26};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    pinMode(LED_PINS[i], OUTPUT);
  }
  Serial.println("예제3: 버튼을 누르는 동안 LED ON");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    bool pressed = (digitalRead(BTN_PINS[i]) == LOW);   // 풀업이므로 LOW = 눌림
    digitalWrite(LED_PINS[i], pressed ? HIGH : LOW);
  }
  delay(10);
}

