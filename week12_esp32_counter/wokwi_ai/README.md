# 12주차: Wokwi + 실제 학습한 AI 임계값 조절 사물 카운터

이 프로젝트는 **카메라 이미지 인식이 아니라 초음파 거리 기반 대상 존재 분류**입니다.
Python scikit-learn LogisticRegression을 실제 학습해 얻은 계수를 ESP32 스케치에서 추론합니다.
가변저항은 AI 가중치가 아닌 결정 **임계값 0.30~0.80**을 조절합니다.

## 파일
- [실습 1: diagram.json](workbook1/diagram.json) / [sketch.ino](workbook1/sketch.ino)
- [실습 2: diagram.json](workbook2/diagram.json) / [sketch.ino](workbook2/sketch.ino)
- [모델 데이터](model/samples.csv) / [학습 코드](model/train_model.py) / [평가 코드](model/evaluate.py) / [가중치](model/model_weights.json)
- [Google Drive 전체 프로젝트 ZIP](https://drive.google.com/file/d/1GFTcW5Ui-NymPC6QW3a0_4okiuPvcPWj/view?usp=drivesdk) (워크북·Colab 노트북 포함)

## Wokwi My Projects에 복사 (로그인 필요)
1. https://wokwi.com/projects/new/esp32 에서 새 프로젝트를 생성합니다.
2. `diagram.json` 탭을 열고 해당 워크북의 `diagram.json` 전체를 붙여 넣습니다.
3. `sketch.ino` 탭을 열고 해당 워크북의 `sketch.ino` 전체를 붙여 넣습니다.
4. 외부 라이브러리 설치는 필요 없습니다(Arduino ESP32 코어와 math.h).
5. Start Simulation으로 컴파일·실행 → 초음파 센서 거리(180→20→180→20cm), 임계값 다이얼, RESET 및 부저를 확인합니다.
6. Save Project하여 자신의 My Projects에 생성된 URL을 복사합니다.
7. [Notion 결과보고](https://app.notion.com/p/41cb2e6bf807808da750ff4a5df05285)에 화면과 결과표를 제출합니다.

## Wokwi 결선
ESP32-DevKitC V4: HC-SR04 TRIG GPIO26 / ECHO GPIO27 / VCC 5V / GND 공통;
Threshold potentiometer SIG GPIO34 / VCC 3V3 / GND; button GPIO18↔GND; LED GPIO23→220Ω→LED A, LED C→GND; buzzer GPIO25→(+) / (-)→GND.
실습2 추가: 가상 마이크 **대체 가변저항** SIG GPIO35 / VCC 3V3 / GND.
**실제 HC-SR04의 ECHO 5V 레벨은 ESP32 GPIO에 직접 인가하면 안 됩니다.** 실물에서는 분압·레벨 시프터가 필요합니다.

## 핵심 코드
- `LogisticRegression.fit`(scikit-learn): PC에서 AI 파라미터 학습
- `sigmoid(b+w×distance)`(ESP32): 학습 결과로 confidence 추론
- `analogRead(34)`: 임계값 다이얼
- `pulseIn(27,HIGH,26000)`: 센서 ECHO 펄스 측정
- `tone(25,frequency,duration)`: Wokwi 부저 알림
- `precision/recall/F1`: test 데이터 성능 계산. train 데이터 평가가 아님.

## 검증 상태
회로 JSON 구조, 일치된 GPIO, 모델 학습 재현성, Python F1 4개 자동 테스트 통과.
일반 g++ 스텁 기반 C++ 구문 검사 통과. **Wokwi 계정에서 실제 컴파일·실행은 아직 미확인.**
