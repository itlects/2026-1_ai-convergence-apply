/*
  9주차 예제 4 — 부저로 도레미파 소리 내기 (주파수 출력)
  보드 : ESP32-DevKitC V4 ("ESP32 Dev Module")

  연결
    수동(패시브) 부저 (+) ── GPIO27
    수동(패시브) 부저 (-) ── GND
    * 3핀 부저 모듈이면: S(또는 I/O) → GPIO27, VCC → 3V3, GND → GND

  원리 : tone(핀, 주파수Hz, 시간ms) 는 핀을 1초에 '주파수' 번 HIGH/LOW로 바꾸는 사각파를 만든다.
         진동판이 같은 횟수로 떨려 그 높이의 소리가 난다. (도=262Hz, 레=294Hz, 미=330Hz, 파=349Hz)
  주의 : '능동(액티브)' 부저는 전원만 주면 한 가지 소리가 나는 부품이라 음 높이가 바뀌지 않는다.
         (부저 뒷면에 초록 기판이 보이면 대체로 수동, 검은 수지로 막혀 있으면 대체로 능동)
*/

const int BUZZER_PIN = 27;
const int NOTES[4]   = {262, 294, 330, 349};          // 도 레 미 파
const char* NAMES[4] = {"도", "레", "미", "파"};

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.println("예제4: 부저 도레미파 (2초마다 반복)");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    Serial.printf("%s  %d Hz\n", NAMES[i], NOTES[i]);
    tone(BUZZER_PIN, NOTES[i], 250);                  // 0.25초 동안 소리
    delay(300);                                       // tone은 바로 다음 줄로 넘어가므로 기다려 준다
  }
  noTone(BUZZER_PIN);
  delay(2000);
}
