#!/bin/bash
# PC에서 ESP32 스케치의 문법·로직을 점검하는 시뮬레이션 (실제 보드 컴파일을 대신하지 않음)
# 필요: g++, ArduinoJson 7 소스 (git clone https://github.com/bblanchon/ArduinoJson)
# 사용: AJSON=../ArduinoJson/src ./run.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
E=$H/../../esp32
export DATA_ROOT=$H/../../dataset/week10_fruits
for ex in ex1_circuit_check ex2_wifi_https_image ex3_vision_labels ex4_vision_classifier; do
  extra=""
  [ $ex = ex2_wifi_https_image ] && extra="downloadAndShow(1);"
  [ $ex = ex4_vision_classifier ] && extra="classifyOne(6,true); evaluateAll();"
  printf '#include "Arduino.h"\n#include "%s/%s/%s.ino"\nint main(){ Serial.input="TESTKEY12345\\n"; setup(); %s return 0; }\n' "$E" $ex $ex "$extra" > /tmp/run_$ex.cpp
  g++ -std=gnu++17 -Wall -Wextra -Wno-unused-parameter -I"$H" -I"$AJSON" -include Arduino.h /tmp/run_$ex.cpp "$H/mock.cpp" -o /tmp/run_$ex
  /tmp/run_$ex > "$E/expected_serial/$ex.txt"
  echo "OK $ex"
done
