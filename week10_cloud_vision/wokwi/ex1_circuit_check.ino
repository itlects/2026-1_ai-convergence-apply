/*
  10주차 예제 1 — 분류 결과 표시 회로 점검 (Wi-Fi 없이 동작)
  보드 : ESP32-DevKitC V4  (Arduino IDE 보드 선택: "ESP32 Dev Module")

  9주차 예제5 회로를 그대로 다시 사용한다. (그림: diagrams/03_wiring_devkitc.png)
    LED1 GPIO32 = apple  (사과)    ── 220Ω ── LED(+) / LED(-) ── GND
    LED2 GPIO33 = banana (바나나)
    LED3 GPIO25 = orange (오렌지)
    LED4 GPIO26 = lemon  (레몬)
    BTN1 GPIO23 = [다음]  1장 분류      ── 버튼 ── GND  (INPUT_PULLUP)
    BTN2 GPIO22 = [전체]  시험 데이터 전체 평가
    (BTN3 GPIO21, BTN4 GPIO19 는 9주차 회로에 꽂혀 있어도 이번 주에는 사용하지 않는다)
    BUZZER GPIO27 ── 100Ω ── 수동 피에조(+) / (-) ── GND

  동작
    1) 부팅하면 LED1→LED4 순서로 한 번씩 켜지며 "어느 LED가 어느 과일인지" 시리얼에 표시한다.
    2) BTN1을 누르면 다음 과일 LED로 넘어가며 '삑'(정답음) 소리를 낸다.
    3) BTN2를 누르면 '삑-삑'(오답음) 소리와 함께 LED 4개가 함께 깜빡인다(= unknown 표시).
    예제 4에서 이 신호(LED 1개 = 예측 클래스, 4개 깜빡임 = unknown, 소리 = 정답/오답)를 그대로 쓴다.
*/

const int LED_PINS[4] = {32, 33, 25, 26};
const char* CLASS_NAMES[4] = {"apple", "banana", "orange", "lemon"};
const int BTN_NEXT = 23;
const int BTN_ALL = 22;
const int BUZZER_PIN = 27;
const unsigned long DEBOUNCE_MS = 30;

int current = 0;

// ---------- 버튼: 디바운스 + 누르는 순간(하강 에지)만 true ----------
struct Button {
  int pin;
  int stable;
  int last;
  unsigned long changedAt;
};

Button btnNext = {BTN_NEXT, HIGH, HIGH, 0};
Button btnAll = {BTN_ALL, HIGH, HIGH, 0};

bool pressed(Button& b) {
  int reading = digitalRead(b.pin);
  unsigned long now = millis();

  if (reading != b.last) {
    b.last = reading;
    b.changedAt = now;
  }

  if ((now - b.changedAt) >= DEBOUNCE_MS && reading != b.stable) {
    b.stable = reading;
    return b.stable == LOW;
  }
  return false;
}

// ---------- 표시 함수 (예제 4와 동일) ----------
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
  tone(BUZZER_PIN, 1047, 120);           // 높은 '삑' 한 번
}

void beepWrong() {
  tone(BUZZER_PIN, 262, 120);            // 낮은 '삑' 두 번
  delay(180);
  tone(BUZZER_PIN, 262, 120);
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
  Serial.println("=== 10주차 예제1: 분류 결과 표시 회로 점검 ===");
  for (int i = 0; i < 4; i++) {
    showClass(i);
    Serial.printf("LED%d (GPIO%d) = %s\n", i + 1, LED_PINS[i], CLASS_NAMES[i]);
    delay(400);
  }
  showClass(current);
  Serial.println("BTN1(GPIO23)=다음 LED + 정답음, BTN2(GPIO22)=unknown 깜빡임 + 오답음");
}

void loop() {
  if (pressed(btnNext)) {
    current = (current + 1) % 4;
    showClass(current);
    beepCorrect();
    Serial.printf("[BTN1] 표시 클래스 -> %s (LED%d)\n", CLASS_NAMES[current], current + 1);
  }

  if (pressed(btnAll)) {
    Serial.println("[BTN2] unknown 표시 테스트 (LED 4개 3회 깜빡임)");
    beepWrong();
    blinkUnknown();
    showClass(current);
  }
}
