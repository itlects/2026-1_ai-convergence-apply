// ESP32-DevKitC V4; Arduino-ESP32 3.x
const int POT = 34;
const int BTN = 18;
const int LED = 23;
int lastBtn = HIGH;
int accepted = 0;
int triggers = 0;
unsigned long lastEdge = 0;
unsigned long lastReport = 0;
String inputLine;

void setup() {
  Serial.begin(115200);
  pinMode(BTN, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
  analogReadResolution(12);
  Serial.println("READY,WB1");
}

void loop() {
  int threshold = map(analogRead(POT), 0, 4095, 30, 95);
  if (millis() - lastReport >= 250) {
    lastReport = millis();
    Serial.printf("THR,%d\n", threshold);
  }

  int button = digitalRead(BTN);
  if (button != lastBtn && millis() - lastEdge >= 40) {
    lastEdge = millis();
    lastBtn = button;
    if (button == LOW) {
      ++triggers;
      Serial.printf("TRIGGER,%d\n", triggers);
    }
  }

  while (Serial.available()) {
    char ch = (char) Serial.read();
    if (ch == '\n') {
      inputLine.trim();
      if (inputLine.startsWith("SCORE,")) {
        float score = inputLine.substring(6).toFloat();
        if (score >= 0.0f && score <= 1.0f) {
          bool hit = score * 100.0f >= threshold;
          if (hit) ++accepted;
          digitalWrite(LED, hit ? HIGH : LOW);
          Serial.printf("RESULT,%.3f,%d,%d\n", score, hit ? 1 : 0, accepted);
        }
      }
      inputLine = "";
    } else if (ch != '\r' && inputLine.length() < 60) {
      inputLine += ch;
    }
  }
}
