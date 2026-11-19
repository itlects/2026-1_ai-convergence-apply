// ESP32 DevKit: GPIO 23 -> 220 ohm -> LED anode, cathode -> GND
const int LED_PIN = 23;
void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
}
void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '1') digitalWrite(LED_PIN, HIGH);
    if (c == '0') digitalWrite(LED_PIN, LOW);
  }
}
