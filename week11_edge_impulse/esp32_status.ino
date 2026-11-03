#include <Arduino.h>
// ESP32-DevKitC V4, Arduino-ESP32 core 3.x
// PC -> ESP32: READY/BUSY/OK/ERROR/DONE followed by newline
// ESP32 -> PC: CAPTURE followed by newline
constexpr int READY_LED=18, WORK_LED=19, ERROR_LED=21, BUTTON=23, BUZZER=25;
String state="READY", line="";
unsigned long since=0, lastPress=0;
bool wasPressed=false;
void beep(int hz,int ms) {
  ledcWriteTone(BUZZER,hz);
  delay(ms);
  ledcWriteTone(BUZZER,0);
}
void setState(String s) {
  if(s!="READY"&&s!="BUSY"&&s!="OK"&&s!="ERROR"&&s!="DONE") return;
  state=s;
  since=millis();
  if(s=="OK") beep(1250,80);
  if(s=="ERROR") { beep(370,110); delay(60); beep(370,110); }
  if(s=="DONE") beep(850,160);
  Serial.println("STATE:"+state);
}
void setup() {
  Serial.begin(115200);
  pinMode(READY_LED,OUTPUT);
  pinMode(WORK_LED,OUTPUT);
  pinMode(ERROR_LED,OUTPUT);
  pinMode(BUTTON,INPUT_PULLUP);
  ledcAttach(BUZZER,2000,8);
  setState("READY");
}
void loop() {
  while(Serial.available()) {
    char c=(char)Serial.read();
    if(c=='\n') { line.trim(); setState(line); line=""; }
    else if(c!='\r' && line.length()<24) line+=c;
  }
  bool pressed=digitalRead(BUTTON)==LOW;
  if(pressed && !wasPressed && millis()-lastPress>=200 && state!="BUSY") {
    lastPress=millis();
    Serial.println("CAPTURE");
  }
  wasPressed=pressed;
  bool blink=(millis()/400)%2==0;
  digitalWrite(READY_LED, state=="READY"||state=="DONE");
  digitalWrite(WORK_LED, state=="OK"||(state=="BUSY"&&blink));
  digitalWrite(ERROR_LED,state=="ERROR");
  if((state=="OK"||state=="ERROR"||state=="DONE") && millis()-since>2200) setState("READY");
}
