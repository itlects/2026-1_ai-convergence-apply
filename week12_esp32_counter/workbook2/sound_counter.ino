// Classic ESP32-DevKitC V4 only (ESP32-WROOM).
const int MIC = 35;
const int POT = 34;
const int DAC_OUT = 25;
const int LED = 23;
const int RESET = 18;
int events = 0;
int lastButton = HIGH;
unsigned long lastEvent = 0;
unsigned long lastLog = 0;
unsigned long lastDebounce = 0;

void beep() {
  for (int i = 0; i < 80; ++i) {
    dacWrite(DAC_OUT, 220);
    delayMicroseconds(500);
    dacWrite(DAC_OUT, 35);
    delayMicroseconds(500);
  }
  dacWrite(DAC_OUT, 128);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  pinMode(RESET, INPUT_PULLUP);
  analogReadResolution(12);
  dacWrite(DAC_OUT, 128);
  Serial.println("READY,WB2");
}

void loop() {
  int threshold = map(analogRead(POT), 0, 4095, 100, 1500);
  int lo = 4095;
  int hi = 0;
  unsigned long started = millis();
  while (millis() - started < 20) {
    int sample = analogRead(MIC);
    if (sample < lo) lo = sample;
    if (sample > hi) hi = sample;
  }
  int peakToPeak = hi - lo;

  if (peakToPeak >= threshold && millis() - lastEvent >= 600) {
    lastEvent = millis();
    ++events;
    digitalWrite(LED, HIGH);
    Serial.printf("EVENT,%d,%d,%d\n", events, peakToPeak, threshold);
    beep();
  } else {
    digitalWrite(LED, LOW);
  }

  int button = digitalRead(RESET);
  if (button != lastButton && millis() - lastDebounce >= 40) {
    lastDebounce = millis();
    lastButton = button;
    if (button == LOW) {
      events = 0;
      Serial.println("RESET,0");
    }
  }
  if (millis() - lastLog >= 500) {
    lastLog = millis();
    Serial.printf("LEVEL,%d,%d,%d\n", peakToPeak, threshold, events);
  }
}
