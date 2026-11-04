/* Week09 example 5 - latest lecture pin map; formatted for readability.
 * LEDs: 32,33,25,26 through 220 ohm; buttons: 23,22,21,19 to GND.
 * Passive low-current piezo: GPIO27 through 100 ohm to +; - to GND.
 */
#include <Arduino.h>

const int BTN_PINS[4] = {23, 22, 21, 19};
const int LED_PINS[4] = {32, 33, 25, 26};
const int BUZZER_PIN = 27;
const int ON_TONE[4] = {523, 659, 784, 1047};
const int OFF_TONE = 196;
const unsigned long DEBOUNCE_MS = 30;

bool ledOn[4] = {false, false, false, false};
int stableState[4] = {HIGH, HIGH, HIGH, HIGH};
int lastReading[4] = {HIGH, HIGH, HIGH, HIGH};
unsigned long changedAt[4] = {0, 0, 0, 0};

void printState() {
  Serial.print(" | state: ");
  for (int i = 0; i < 4; i++) {
    Serial.print(ledOn[i] ? '1' : '0');
  }
  Serial.println();
}

void playAllOn() {
  const int melody[] = {523, 659, 784, 1047};
  for (int n : melody) {
    tone(BUZZER_PIN, n, 120);
    delay(140);
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  pinMode(BUZZER_PIN, OUTPUT);
  tone(BUZZER_PIN, 880, 100);
  Serial.println("Week09 smart panel ready");
}

void loop() {
  const unsigned long now = millis();
  for (int i = 0; i < 4; i++) {
    const int reading = digitalRead(BTN_PINS[i]);
    if (reading != lastReading[i]) {
      lastReading[i] = reading;
      changedAt[i] = now;
    }
    if ((now - changedAt[i]) >= DEBOUNCE_MS &&
        reading != stableState[i]) {
      stableState[i] = reading;
      if (stableState[i] == LOW) {
        ledOn[i] = !ledOn[i];
        digitalWrite(LED_PINS[i], ledOn[i] ? HIGH : LOW);
        tone(BUZZER_PIN, ledOn[i] ? ON_TONE[i] : OFF_TONE, 80);
        Serial.printf("[BTN%d] LED%d %s", i + 1, i + 1,
                      ledOn[i] ? "ON" : "OFF");
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
