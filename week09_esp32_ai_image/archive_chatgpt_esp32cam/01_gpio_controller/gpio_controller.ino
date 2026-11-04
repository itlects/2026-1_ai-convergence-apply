/*
 * Week09 / Workbook 1
 * ESP32-DevKitC V4 (ESP32-WROOM-32) / Arduino-ESP32 3.x
 * LEDs: GPIO 16,17,18,19 -> 330ohm -> LED anode; cathode -> GND
 * Buttons: GPIO 13,14,25,26 -> button -> GND (INPUT_PULLUP)
 * Passive low-current piezo: GPIO 27 -> 100ohm -> piezo+ ; piezo- -> GND
 * For magnetic/high-current buzzers, use a transistor driver instead.
 */
#include <Arduino.h>

const uint8_t LED_PINS[4] = {16, 17, 18, 19};
const uint8_t BTN_PINS[4] = {13, 14, 25, 26};
const uint8_t BUZZER_PIN = 27;

bool stableState[4] = {HIGH, HIGH, HIGH, HIGH};
bool lastReading[4] = {HIGH, HIGH, HIGH, HIGH};
unsigned long changedAt[4] = {0, 0, 0, 0};
bool ledState[4] = {false, false, false, false};
const unsigned long DEBOUNCE_MS = 35;

void beep(uint16_t frequency, uint16_t durationMs) {
  tone(BUZZER_PIN, frequency, durationMs);
}

void onPressed(uint8_t index) {
  ledState[index] = !ledState[index];
  digitalWrite(LED_PINS[index], ledState[index] ? HIGH : LOW);
  beep(700 + 200 * index, 100);
  Serial.printf("Button %u: LED %u = %s\n",
                index + 1, index + 1,
                ledState[index] ? "ON" : "OFF");
}

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < 4; ++i) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    lastReading[i] = digitalRead(BTN_PINS[i]);
    stableState[i] = lastReading[i];
  }
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.println("Week09 GPIO controller ready");
}

void loop() {
  const unsigned long now = millis();
  for (uint8_t i = 0; i < 4; ++i) {
    const bool reading = digitalRead(BTN_PINS[i]);
    if (reading != lastReading[i]) {
      changedAt[i] = now;
      lastReading[i] = reading;
    }
    if (now - changedAt[i] >= DEBOUNCE_MS &&
        reading != stableState[i]) {
      stableState[i] = reading;
      if (stableState[i] == LOW) {
        onPressed(i);
      }
    }
  }
}