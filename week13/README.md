# 13주 — AI 음성 라벨링과 RAG 지식 추가

## Workbook 1 (Windows)
1. ZIP 압축 해제, Windows 터미널에서 `week13` 폴더로 이동.
2. `py -m http.server 8000` 실행. Chrome/Edge에서 `http://localhost:8000/app.html` 접속.
3. 빨강/파랑 샘플 버튼으로 분류 확인. 카메라 시작 후 색종이를 중앙에 제시. RGB 평균 기반 최근접 중심 분류이며 물체 종류를 판단하지 않는다.
4. 인식 확정 버튼을 눌러 카운터와 화면 LED 확인. 녹음 시작→한 문장 말하기→녹음 종료→WAV 재생 및 다운로드.
5. STT 버튼을 눌러 같은 문장을 다시 말한다(브라우저 음성인식 서비스, 네트워크 및 동의 필요). 이 기능은 저장한 WAV를 직접 변환하지 않는다. 미지원 시 녹음을 듣고 직접 입력. 교정 후 저장.
6. 파랑/빨강 두 건 반복. 검색창에서 라벨 입력→근거 출력, 답변 읽기→스피커 소리 확인. JSONL 다운로드.
7. 선택: ESP32 DevKit GPIO23 → 220Ω → LED 긴 다리, LED 짧은 다리 → GND. Arduino IDE에서 esp32_led.ino 업로드. 시리얼 모니터 닫고 페이지의 ESP32 LED 연결을 클릭, USB 포트 선택(Chrome/Edge Web Serial 지원 필요). 확정 시 켜짐, 지식 저장 시 꺼짐.

## Workbook 2 (Colab)
- Drive에서 sample_knowledge.jsonl 및 sample_1.wav 다운로드. 학생용 WB2_student.ipynb을 Colab에서 연 뒤 본인 Drive에 사본 저장. CPU 런타임 사용.
- 셀을 순서대로 실행. 준비된 영어 합성 음성은 참조 전사와 함께 제공. 실제 음성인식은 WB1의 STT로 수행.
- 파일 창의 업로드 버튼으로 WB1 field_knowledge.jsonl을 업로드하고 추가 셀을 실행. 키워드 검색 결과 비교 후 rag_knowledge.jsonl 다운로드.
- 강의자는 WB2_teacher.ipynb을 사용. 이 실습은 LLM 학습/재학습이 아니라 검색용 지식베이스 갱신이다.

## 데이터
- sample_knowledge.jsonl: 교육용 가상 현장 데이터 3건. id, label, text(한국어 지식), source, verified, reference_en(영어 음성 참조 전사).
- sample_1~3.wav: 합성 영어 음성, 16kHz 모노 PCM. 실제 개인정보 없음.
- field_knowledge.jsonl: 학생이 생성한 데이터. 소스 WAV는 직접 다운로드해야 한다. 학생 자신의 데이터는 공개 저장소에 올리지 말 것.
