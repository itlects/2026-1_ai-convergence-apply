# 워크북 1 — 스마트 제어 패널 (ESP32-DevKitC V4)

## 완성 목표
버튼 1~4를 누를 때 LED 1~4가 각각 토글되고 서로 다른 높이의 비프음이 납니다. 버튼을 길게 눌러도 1회만 토글되어야 합니다.

## 준비물
ESP32-DevKitC V4 1개, LED 4개, 330Ω 저항 4개, 순간 버튼 4개, 저전류 수동 피에조 부저 1개, 100Ω 저항 1개, 브레드보드, 점퍼선, USB 케이블.

## 이론 키워드
| 키워드 | 의미 | 코드 예 |
|---|---|---|
| GPIO | 범용 디지털 핀 | 16, 17, 18, 19 |
| OUTPUT | 핀 출력 | `pinMode(16, OUTPUT)` |
| INPUT_PULLUP | 내부 풀업으로 평소 HIGH, 누르면 LOW | `pinMode(13, INPUT_PULLUP)` |
| digitalRead | 버튼 상태 읽기 | `digitalRead(13)` |
| digitalWrite | LED 켜고 끄기 | `digitalWrite(16, HIGH)` |
| millis | 경과시간으로 채터링 제거 | `millis()` |
| tone | 수동 피에조 음 발생 | `tone(27, 880, 100)` |

## 배선표
| 부품 | ESP32 핀 | 나머지 연결 |
|---|---|---|
| LED1 | GPIO16 → 330Ω → LED(+) | LED(-) → GND |
| LED2 | GPIO17 → 330Ω → LED(+) | LED(-) → GND |
| LED3 | GPIO18 → 330Ω → LED(+) | LED(-) → GND |
| LED4 | GPIO19 → 330Ω → LED(+) | LED(-) → GND |
| BTN1 | GPIO13 | 버튼 반대쪽 GND |
| BTN2 | GPIO14 | 버튼 반대쪽 GND |
| BTN3 | GPIO25 | 버튼 반대쪽 GND |
| BTN4 | GPIO26 | 버튼 반대쪽 GND |
| 저전류 수동 피에조 | GPIO27 → 100Ω → (+) | (-) → GND |

**중요:** 버튼 4개 다리의 내부 연결을 확인하세요. 브레드보드 한쪽 레일에 같은 접점 두 다리를 꽂으면 버튼이 상시 눌린 것으로 보일 수 있습니다. 배선 중 USB 전원을 분리합니다. GPIO는 3.3V 신호만 사용합니다.

## 실행 순서
1. 회로 연결을 확인하고 USB로 ESP32를 PC에 연결합니다.
2. Arduino IDE의 보드 매니저에서 Espressif ESP32를 설치하고 보드를 `ESP32 Dev Module`로 선택합니다.
3. [전체 소스](./01_gpio_controller/gpio_controller.ino)를 복사해 `gpio_controller.ino`로 저장합니다.
4. 업로드한 다음 직렬 모니터 115200 baud를 설정합니다.
5. 버튼 1~4를 차례로 한 번 누르고, 다시 눌러 LED가 꺼지는지 확인합니다.
6. 각 버튼을 2초간 눌러 중복 토글이 없는지 확인합니다.

## 예상 실행 결과
```text
Week09 GPIO controller ready
Button 1: LED 1 = ON
Button 2: LED 2 = ON
Button 1: LED 1 = OFF
```

## 실습 결과 기록
| 항목 | 예상 결과 | 실제 결과 / 사진 |
|---|---|---|
| 버튼1 | LED1 토글, 700Hz 음 | |
| 버튼2 | LED2 토글, 900Hz 음 | |
| 버튼3 | LED3 토글, 1100Hz 음 | |
| 버튼4 | LED4 토글, 1300Hz 음 | |
| 길게 누르기 | 중복 토글되지 않음 | |

## 탐구 문제
1. 내부 풀업 모드에서 버튼을 누르면 왜 LOW인가요?
2. `delay(50)` 대신 `millis()`를 사용한 이유는 무엇인가요?
3. 저항 없이 LED를 연결하면 어떤 문제가 생기나요?
4. 버튼 하나로 LED 4개를 모두 끄는 기능을 설계해보세요.

## 제출
실물 회로 사진, 코드 변경사항, 직렬 로그, 검증표, 질문 답변을 제출합니다.
