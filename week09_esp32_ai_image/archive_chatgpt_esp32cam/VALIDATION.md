# 9주차 코드 검증 기록 (2026-11-03)

| 항목 | 검증 방식 | 결과 |
|---|---|---|
| gallery.html JavaScript 파싱 | V8 `new Function` 문법 검사 | PASS |
| 96×96 변환 | Canvas width/height와 drawImage center crop 정적 점검 | PASS (동적 브라우저 실행 미검증) |
| GPIO 핀 매핑 | LED 16/17/18/19, 버튼 13/14/25/26, 부저 27 확인 | PASS |
| INPUT_PULLUP와 debounce | 35ms 비차단 버튼 상태 변경 확인 | PASS (실물 미검증) |
| 카메라 프레임 반환 | `esp_camera_fb_return` 경로 확인 | PASS |
| SD 1-bit 모드 | `SD_MMC.begin("/sdcard", true)` 확인 | PASS |
| 초기화 실패 보호 | 카메라+SD 초기화 후에만 촬영 허용 | PASS |
| ESP32 DevKitC 컴파일 | 실제 Arduino-ESP32 툴체인 / 실보드 없음 | **미실시** |
| ESP32-CAM 컴파일·촬영 | 실제 Arduino-ESP32 툴체인 / 실보드 없음 | **미실시** |
| 전기 배선·음량 검증 | 실부품/오실로스코프 확인 필요 | **미실시** |

정적 점검은 컴파일·실행 확인과 같지 않습니다. 강의 전 사용 중인 Arduino-ESP32 코어 버전(예: 3.x), 실제 보드 리비전과 부저 소비전류를 기준으로 컴파일·업로드·배선 검증을 완료해야 합니다.
