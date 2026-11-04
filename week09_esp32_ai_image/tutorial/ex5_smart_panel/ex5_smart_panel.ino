/*
  9주차 예제 5 (종합) — 버튼 4개 · LED 4개 · 부저 "스마트 제어 패널"
  보드 : ESP32-DevKitC V4 ("ESP32 Dev Module")

  연결 요약 (그림: diagrams/09_wiring_full_devkitc.png)
    LED1~4  : GPIO32, 33, 25, 26  ── 220Ω ── LED(+) / LED(-) ── GND
    BTN1~4  : GPIO23, 22, 21, 19  ── 버튼 ── GND   (INPUT_PULLUP)
    BUZZER  : GPIO27 ── 부저(+) / 부저(-) ── GND

  동작
    - 버튼 N을 한 번 누를 때마다 LED N이 ON ↔ OFF 로 바뀐다(토글).
    - ON 이 될 때는 버튼별로 다른 높이의 '삑', OFF 가 될 때는 낮은 '뚝' 소리.
    - LED 4개가 모두 켜지면 축하 멜로디 + 시리얼에 "ALL ON" 출력.
    - 시리얼 모니터에 버튼 이벤트와 LED 상태가 기록된다.  예) [BTN2] LED2 ON  | 상태: 0100

  핵심 개념 : 채터링(바운싱) 제거
    버튼 금속판은 눌리는 순간 수 ms 동안 붙었다 떨어졌다를 반복한다.
    그대로 읽으면 한 번 눌렀는데 여러 번 눌린 것처럼 토글된다.
    → 상태가 바뀐 뒤 DEBOUNCE_MS(30ms) 동안 그대로 유지될 때만 '진짜 변화'로 인정한다.
    → 그리고 HIGH→LOW(누르는 순간, 하강 에지) 한 번만 토글한다. (누르고 있어도 반복 토글되지 않음)
*/

const int BTN_PINS[4] = {23, 22, 21, 19};
const int LED_PINS[4] = {32, 33, 25, 26};
const int BUZZER_PIN  = 27;
const int ON_TONE[4]  = {523, 659, 784, 1047};   // 도5 미5 솔5 도6
const int OFF_TONE    = 196;                     // 낮은 솔
const unsigned long DEBOUNCE_MS = 30;

bool ledOn[4]            = {false, false, false, false};
int  stableState[4]      = {HIGH, HIGH, HIGH, HIGH};   // 확정된 버튼 상태
int  lastReading[4]      = {HIGH, HIGH, HIGH, HIGH};   // 직전에 읽은 값
unsigned long changedAt[4] = {0, 0, 0, 0};             // 읽은 값이 마지막으로 바뀐 시각

void printState() {
  Serial.print(" | 상태: ");
  for (int i = 0; i < 4; i++) Serial.print(ledOn[i] ? '1' : '0');
  Serial.println();
}

void playAllOn() {
  const int melody[] = {523, 659, 784, 1047};
  for (int n : melody) { tone(BUZZER_PIN, n, 120); delay(140); }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  pinMode(BUZZER_PIN, OUTPUT);
  tone(BUZZER_PIN, 880, 100);                    // 부팅 완료 알림음
  Serial.println("\n예제5: 스마트 제어 패널 준비 완료 — 버튼을 눌러 보세요");
}

void loop() {
  unsigned long now = millis();

  for (int i = 0; i < 4; i++) {
    int reading = digitalRead(BTN_PINS[i]);

    if (reading != lastReading[i]) {             // 값이 흔들리면 타이머 다시 시작
      lastReading[i] = reading;
      changedAt[i] = now;
    }

    // 30ms 이상 같은 값이 유지되었고, 확정 상태와 다르면 → 진짜 변화
    if ((now - changedAt[i]) >= DEBOUNCE_MS && reading != stableState[i]) {
      stableState[i] = reading;

      if (stableState[i] == LOW) {               // 누르는 순간(하강 에지)에만 실행
        ledOn[i] = !ledOn[i];
        digitalWrite(LED_PINS[i], ledOn[i] ? HIGH : LOW);
        tone(BUZZER_PIN, ledOn[i] ? ON_TONE[i] : OFF_TONE, 80);

        Serial.printf("[BTN%d] LED%d %s", i + 1, i + 1, ledOn[i] ? "ON " : "OFF");
        printState();

        if (ledOn[0] && ledOn[1] && ledOn[2] && ledOn[3]) {
          Serial.println("*** ALL ON ***");
          delay(100);
          playAllOn();
        }
      }
    }
  }
}

