// 12주차 Wokwi ESP32 AI 사물 존재 분류 (카메라 인식 아님)
// 실제로 학습한 LogisticRegression 계수를 사용합니다.
#include <Arduino.h>
#include <math.h>
const int TRIG=26, ECHO=27, DIAL=34, LED=23, RESET=18, BUZZER=25;
const float MODEL_BIAS=1.778584554f;
const float MODEL_DISTANCE_WEIGHT=-0.031021410f;
int countObjects=0, goodFrames=0, farFrames=0, previousButton=HIGH;
bool latched=false;
unsigned long lastCycle=0,lastButtonChange=0;

float distanceCm() {
  digitalWrite(TRIG,LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG,HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG,LOW);
  unsigned long pulse=pulseIn(ECHO,HIGH,26000UL);
  return pulse ? pulse/58.0f : 400.0f;
}
float confidenceOf(float d) {
  float z=MODEL_BIAS+MODEL_DISTANCE_WEIGHT*d;
  return 1.0f/(1.0f+expf(-z));
}
float thresholdOf() {
  return 0.30f+0.50f*analogRead(DIAL)/4095.0f;
}
void setup() {
  Serial.begin(115200);
  pinMode(TRIG,OUTPUT);
  pinMode(ECHO,INPUT);
  pinMode(LED,OUTPUT);
  pinMode(RESET,INPUT_PULLUP);
  analogReadResolution(12);
  Serial.println("READY,week12-ai-counter");
}

void loop() {
  int button=digitalRead(RESET);
  if(button!=previousButton && millis()-lastButtonChange>60) {
    lastButtonChange=millis();
    previousButton=button;
    if(button==LOW) {
      countObjects=0;
      latched=false;
      farFrames=0;
      goodFrames=0;
      Serial.println("RESET,0");
    }
  }
  if(millis()-lastCycle<250) return;
  lastCycle=millis();
  float d=distanceCm();
  float p=confidenceOf(d);
  float threshold=thresholdOf();
  bool detected=p>=threshold;
  digitalWrite(LED,detected ? HIGH : LOW);
   
  if(d>140.0f) {
    if(++farFrames>=2) {
      latched=false;
      goodFrames=0;
    }
  } else {
    farFrames=0;
  }
  if(!latched && detected && d<=140.0f) {
    if(++goodFrames>=2) {
      countObjects++;
      latched=true;
      goodFrames=0;
      tone(BUZZER,880,100);
      Serial.printf("COUNT,%d\n",countObjects);
    }
  } else if(!detected) {
    goodFrames=0;
  }
  Serial.printf("DATA,%.1f,%.3f,%.3f,%d,%d\n",d,p,threshold,detected?1:0,countObjects);
}
