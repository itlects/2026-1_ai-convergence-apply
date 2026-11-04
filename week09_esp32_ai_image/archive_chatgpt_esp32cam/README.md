# 9주차: 인공지능 학습 모델 준비하기 ①

> 8주차는 중간고사. 9주차는 GPIO → 카메라 JPEG → SD → 96×96 전처리 → 갤러리 순서.

## 소스와 워크북
- [워크북 1: GPIO 제어](./WORKBOOK_1_GPIO.md)
- [워크북 2: 카메라·SD·갤러리](./WORKBOOK_2_CAMERA_GALLERY.md)
- [ESP32-DevKitC V4 GPIO 코드](./01_gpio_controller/gpio_controller.ino)
- [AI Thinker ESP32-CAM 코드](./02_camera_sd/camera_sd.ino)
- [이미지 갤러리 앱](./03_gallery/gallery.html) — 내려받아 Chrome/Edge에서 열기

## 주의: 카메라 보드 구분
ESP32-DevKitC V4 (일반 WROOM형)에 OV2640 카메라를 꽂는 소켓이 있는 것이 아닙니다. GPIO 실습에는 DevKitC V4를, 카메라+microSD에는 별도 AI Thinker ESP32-CAM을 사용합니다. 두 보드를 직접 전기적으로 연결하지 않는 독립 단계입니다. ESP32-CAM 보드에는 USB-UART 업로더와 안정적인 5V 전원, FAT32 microSD가 필요합니다.

## 권장 핀
LED: 16,17,18,19 (각 330Ω 직렬). 버튼: 13,14,25,26 (GND로 누르는 버튼 INPUT_PULLUP). 수동 저전류 피에조: 27 (100Ω 직렬). 전류 소모가 큰 부저는 트랜지스터 드라이버를 사용. 3.3V GPIO에 5V 직접 입력 금지.

## 실습 산출물
버튼 4개 동작 기록표, 직렬 모니터 로그, SD의 JPEG 3장, 이미지 크기·파일크기 표, 96×96 PNG 3장, 갤러리 화면 캡처, 학습 데이터 라벨링 계획.

## 검증 범위
이미지 갤러리 코드 구조 및 API를 점검하되, 실제 ESP32 보드 컴파일 및 실물 회로 검증은 장비가 연결된 실습 PC에서 별도 수행해야 합니다. 학생/강의자는 Arduino-ESP32 3.x 환경에서 업로드 후 직렬 모니터로 검증합니다.

참고: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html
