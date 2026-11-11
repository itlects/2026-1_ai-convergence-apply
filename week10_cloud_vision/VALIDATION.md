# 10주차 검증 기록 — 2026-11-11

## Colab 노트북 (로컬 Jupyter 커널, Python 3.13, scikit-learn 1.9, gdown 6.5)
- 워크북1·2 **완성본**: 처음부터 끝까지 오류 없이 실행 (nbclient).
  - cache 모드: **테스트용 가짜 vision_cache.json**으로 실행 → 노트북의 Vision '실행 결과 미리 보기'는 형식 예시다.
  - none 모드(키·캐시 없음): Vision 단계는 안내 후 건너뛰고 분할·kNN까지 오류 없이 완료.
  - live 모드: `requests.post`를 가짜 응답으로 바꿔 요청 구조(16장씩 5번, LABEL_DETECTION, Base64 JPEG)와 오류 메시지 처리 확인. **실제 Vision API 호출은 하지 않음(키 없음).**
- 워크북1·2 **학생용**: 빈칸(`____`) 셀과 그 결과를 쓰는 다음 셀에서만 NameError (의도된 동작).
- 데이터 다운로드: 이 작업 환경에서는 Drive·GitHub 접근이 막혀 ③ 직접 업로드 경로로 실행. Colab에서는 ①(gdown 폴더)로 받아질 것으로 예상하며, 수업 전 확인 필요.
- 분할·kNN 수치(누구나 같음): train 56 / val 12 / test 12, ESP32 예제4 test 목록과 일치,
  kNN(평균 R·B, val로 k=3 선택) test 0.833, kNN(색 특징 6개) test 1.000.

## ESP32 스케치
- Arduino-ESP32 3.3.8 헤더와 대조: `HTTPClient::begin(NetworkClient&, String)`, `getStreamPtr()`, `setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS)`,
  `base64::encode(const uint8_t*, size_t)`, `NetworkClientSecure::setInsecure()`, `WiFiClient = NetworkClient`, `tone(pin, freq, ms)` 확인.
- PC 시뮬레이션(`tools/esp32_host_test`): Arduino/Wi-Fi/HTTP 를 흉내 낸 헤더 + 실제 ArduinoJson 7.4.2로 4개 스케치를 g++ `-Wall -Wextra` 경고 없이 빌드하고,
  실제 데이터셋 JPEG를 '다운로드'·Base64 변환, 가짜 Vision JSON 해석, 매핑·정확도·혼동행렬, 잘못된 키 오류 메시지까지 실행 확인.
- **실제 ESP32 툴체인 컴파일·보드 업로드·Wi-Fi·Vision 호출은 이 환경에서 불가하여 미실시** → 수업 전 강의자 확인 필요.

## 수업 전 강의자 확인 목록
1. Cloud Vision API 사용 설정 + 수업용 API 키(API 제한) 생성, 예산 알림.
2. `Week10_00_Instructor_VisionCache.ipynb` 실행 → Drive `04_데이터_과일80장`에 `vision_cache.json` 업로드.
3. 실제 Vision 결과로 워크북2의 val 규칙 선택·test 정확도 확인 (미리 보기 값과 다를 수 있음).
4. Arduino IDE에서 ArduinoJson 7 설치 후 예제 2~4 컴파일·업로드, 강의실 Wi-Fi(2.4GHz) 또는 핫스팟 연결 확인.
