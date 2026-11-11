#include <Arduino.h>
const int BUTTON=23,GREEN=18,RED=19;
int previous=HIGH;
unsigned long lastPress=0;
void setup(){
 Serial.begin(115200);
 pinMode(BUTTON,INPUT_PULLUP);
 pinMode(GREEN,OUTPUT);
 pinMode(RED,OUTPUT);
 digitalWrite(GREEN,HIGH);
 digitalWrite(RED,LOW);
}
void loop(){
 int state=digitalRead(BUTTON);
 unsigned long now=millis();
 if(previous==HIGH && state==LOW && now-lastPress>=200){
  lastPress=now;
  digitalWrite(GREEN,LOW);digitalWrite(RED,HIGH);
  Serial.println("CAPTURE_REQUEST");
 }
 previous=state;
 if(Serial.available()){
  String cmd=Serial.readStringUntil('\n');cmd.trim();
  if(cmd=="DONE" || cmd=="RESET"){
   digitalWrite(RED,LOW);digitalWrite(GREEN,HIGH);
   Serial.println("READY");
  }
 }
 delay(10);
}