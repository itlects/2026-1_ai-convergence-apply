# 10주차 — 인공지능 학습모델 준비하기 ② : Cloud Vision 분류 · 정확도 · 학습/검증/시험 데이터 분할

- 강의자료(Notion): https://app.notion.com/p/40db2e6bf80780f0b253edeeb0253a31
- Google Drive: https://drive.google.com/drive/folders/1-5MncyDFgsVcHxzDHO9kBu4MxLHlPgBk
- 보드: **ESP32-DevKitC V4** (Arduino IDE 보드 선택 "ESP32 Dev Module", esp32 by Espressif 3.x)
- 회로: **9주차 예제5 회로(LED 32·33·25·26, 버튼 23·22·21·19, 부저 27)를 그대로 사용**

## 학습 목표
1. 지도학습·비지도학습·강화학습, 분류·회귀를 구분한다.
2. Cloud Vision API(LABEL_DETECTION)로 이미지를 분류하고 정확도를 계산한다.
3. 데이터를 학습(train)·검증(validation)·시험(test)으로 층화 분할하고 각각의 역할에 맞게 사용한다.
4. Vision 라벨을 클래스로 바꾸는 규칙을 검증 데이터로 고르고, 시험 데이터로 1회 평가한다.

## 폴더 구성
| 경로 | 내용 |
| --- | --- |
| `dataset/week10_fruits.zip` | 과일 4종(apple·banana·orange·lemon) x 20장 = 80장, `labels.csv`, `split_seed42.csv` |
| `dataset/week10_fruits/` | 같은 내용(압축 해제본). ESP32가 `raw.githubusercontent.com`에서 이미지를 받는다 |
| `esp32/ex1_circuit_check` | 예제1 회로 점검(LED=클래스, 버튼, 부저) — Wi-Fi 불필요 |
| `esp32/ex2_wifi_https_image` | 예제2 Wi-Fi 연결 + HTTPS 이미지 다운로드 + Base64 |
| `esp32/ex3_vision_labels` | 예제3 ESP32에서 Cloud Vision 직접 호출, 라벨·점수 출력 (ArduinoJson 7) |
| `esp32/ex4_vision_classifier` | 예제4 매핑 규칙 → 4종 분류 → LED·부저 + test 12장 정확도·혼동행렬 |
| `esp32/expected_serial/` | PC 시뮬레이션으로 만든 시리얼 출력 예시 (Vision 응답은 가짜 → 형식 참고용) |
| `colab/Week10_Workbook1_VisionAPI_*.ipynb` | 워크북1 Colab 편: 요청·응답 JSON, Base64, 라벨 확인 |
| `colab/Week10_Workbook2_DataSplit_*.ipynb` | 워크북2: 층화 분할 → 규칙 선택(val) → test 평가 → kNN 직접 학습 비교 |
| `colab/Week10_00_Instructor_VisionCache.ipynb` | 강의자용: 80장 Vision 결과를 `vision_cache.json`으로 저장해 Drive에 업로드 |
| `diagrams/` | 개념도·연결도·회로도 (SVG 원본 + PNG) |
| `screens/` | 노트북 실행 화면 캡처 (Vision 혼동행렬은 형식 예시) |
| `tools/` | 데이터셋·그림·노트북 생성 스크립트, ESP32 PC 시뮬레이션 점검 |
| `archive_chatgpt_draft/` | 이전 ChatGPT 초안 (도형 합성 데이터, 버튼 트리거 방식) — 사용하지 않음 |

## 데이터 다운로드 방식 (실습 시간 절약)
1. **Google Drive** `04_데이터_과일80장` 폴더(ID `1Is7dwskGMYvOxeIRhy0QYMZejj0K8BWE`)를 `gdown.download_folder()`로 받는다.
2. 실패하면 GitHub raw의 `week10_fruits.zip`.
3. 그래도 안 되면 zip을 Colab 왼쪽 파일 창에 직접 업로드.

## API 키 (강의자 준비)
- 수업용 Cloud Vision API 키 1개(API 제한: Cloud Vision API)를 만들어 **수업 시간에만** 전달, 수업 후 삭제.
- 학생 입력: Colab = getpass 입력창 또는 보안 비밀 `VISION_API_KEY` / ESP32 = 시리얼 모니터 입력.
- 키를 Notion·GitHub·Drive 등 공개 자료에 넣지 않는다.
- 키가 없는 학생은 강의자가 만든 `vision_cache.json`(cache 모드)으로 진행, 둘 다 없으면 Vision 단계를 건너뛰고 kNN까지 진행.

## 데이터 출처·라이선스
Fruits-360 dataset (100x100), Mihai Oltean, https://github.com/fruits-360/fruits-360-100x100 — CC BY-SA 4.0.
4개 클래스 각 20장을 고르게 골라 이름만 바꿈. 이 부분집합도 CC BY-SA 4.0. (`dataset/week10_fruits/ATTRIBUTION.txt`)

## 다시 만들기
```bash
python3 tools/build_dataset.py <fruits-360-100x100/Test> dataset
python3 tools/make_wiring.py ../week09_esp32_ai_image/diagrams/08_wiring_full_devkitc.svg diagrams/03_wiring_devkitc.svg
python3 tools/make_schematic.py ../week09_esp32_ai_image/diagrams/09_schematic_full_devkitc.svg diagrams/04_schematic_devkitc.svg
python3 tools/make_diagrams.py diagrams && for f in diagrams/*.svg; do rsvg-convert -z 2 "$f" -o "${f%.svg}.png"; done
python3 tools/build_notebooks.py colab tools/expected_outputs.json
```
검증 기록은 `VALIDATION.md` 참고.
