# 11주차 — Edge Impulse 이미지 분류 + ESP32-DevKitC V4

## 실제 구현 구조
노트북/리눅스 PC 카메라 → Edge Impulse Linux `.eim` 분류 추론 → USB Serial → ESP32-DevKitC V4 → LED·부저. **ESP32 직접 추론이 아닌 PC-ESP32 연동 예제입니다.**

## 회로
- GPIO18 → 220Ω → 초록 LED (+); LED(-) → GND : 준비/종료
- GPIO19 → 220Ω → 노랑 LED (+); LED(-) → GND : 작업 중 점멸/성공
- GPIO21 → 220Ω → 빨강 LED (+); LED(-) → GND : 불확실/오류
- GPIO23 → 버튼 → GND : INPUT_PULLUP
- GPIO25 → 저전류 수동 피에조 (+); (-) → GND
- USB Micro-B 단일 전원. **GPIO에 5V 인가 금지**, LED 직렬 저항 필수.
- DevKitC V4에는 카메라가 없습니다.

## 워크북 1 (50분 이론 + 60분 실습)
1. GPIO 연결과 부품 극성 점검, USB 분리 상태에서 배선.
2. Arduino-ESP32 core **3.x** 설치, `esp32_status.ino` 업로드.
3. 시리얼 모니터 115200, Newline: `READY`, `BUSY`, `OK`, `ERROR`, `DONE`을 보내 LED/부저 상태 확인; 버튼은 `CAPTURE` 전송.
4. SD카드의 10주차 **실제 페트병/캔/종이 사진**을 노트북에 복사. 10주차 제공 도형 이미지 60장은 별도 데모이며 사물 학습용이 아닙니다.
5. Edge Impulse 프로젝트에서 Image classification → Data Acquisition → Upload existing data → Training/Testing → Image processing + Transfer learning → Model testing → Deployment.
6. 클래스 이름은 정확히 `bottle`, `can`, `paper` 사용. 각 클래스 다양한 조명·배경·시점 확보.

## 워크북 2 (70분)
1. Ubuntu / Raspberry Pi 등 Linux에서 Edge Impulse Linux runner로 `model.eim` 다운로드.
2. `pip install -r requirements.txt`
3. `python pc_edge_bridge.py --demo --once` : 모의 확률 테스트.
4. `python pc_edge_bridge.py --model model.eim --port /dev/ttyUSB0` : 카메라·ESP32 실측.
5. 버튼을 눌러 촬영, 라벨/점수/LED/부저 기록. `--threshold 0.60` 변경 후 비교.

**주요 함수** `pinMode`, `INPUT_PULLUP`, `digitalRead`, `digitalWrite`, `millis`, `ledcAttach`, `ledcWriteTone`, `ImageImpulseRunner`, `get_features_from_image`, `classify`, `Serial`.

**정확성 주의**: 빨강 LED의 ERROR는 모델이 실제로 틀렸음을 알려주는 것이 아니라 **신뢰도가 임계값 미만**인 상태입니다. 정확도는 실제 정답과 비교해서만 계산합니다.

**검증**: Python 함수 단위 테스트와 `--demo` 시뮬레이션 통과. 실물 Arduino 컴파일/회로 및 Linux 모델 파일 실추론은 강의 전 보드 환경에서 별도 검증이 필요합니다.

**공유 폴더**: https://drive.google.com/drive/folders/1W8DOwLLUWHn62emVMfD4lzzaPdC112o7
