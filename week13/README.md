# 13주 — 인공지능 학습하기: 음성 라벨링과 추가 지식베이스(RAG)

카메라 인식 결과에 **음성으로 현장 지식**을 붙여 기록하고, 음성을 텍스트로 바꿔 **RAG 추가 지식베이스**를 만든다.
실습은 **Colab + 학생 핸드폰**(사진·녹음·듣기)으로 진행한다. ESP32-S3 CAM은 선택 실습.

## 학생용 노트북 (GitHub에서 열면 항상 새 사본 → 강의자 실행과 분리)
| 워크북 | Colab에서 열기 |
|---|---|
| 워크북 1 — 음성 라벨링 카운터 | https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/week13/WB1_student.ipynb |
| 워크북 2 — 추가 지식베이스와 음성 챗봇 | https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/week13/WB2_student.ipynb |

강의자 시연용: `WB1_teacher.ipynb`, `WB2_teacher.ipynb` (강의자 메모·예상 결과 포함)

## 실습 흐름
1. 학습 사진 10장 → 평균 RGB → 클래스 중심(학습) → 시험 사진 예측(빨강·파랑·미확정)
2. 확정 버튼 → 카운터 +1, LED ON → 녹음(WAV) → Whisper STT → 용어 교정·사람 검토 → JSONL 저장 → LED OFF
3. Gradio 공유 주소(QR)로 핸드폰에서 사진 촬영·녹음·결과 확인
4. 기존 문서 지식 5건 + 음성 지식 → 품질 점검·병합 → `rag_knowledge.jsonl`
5. TF-IDF 글자 n-gram 검색으로 전/후 비교 → 음성 질문 → 답변 → gTTS 음성

## 데이터
`data/week13_data.zip` (Google Drive에도 같은 파일, 노트북은 Drive에서 먼저 받고 실패 시 이 파일 사용)
- images/train/{red,blue} 학습 사진 5장씩, images/test 시험 사진 5장 (합성)
- audio/voice_*.wav 현장 음성 메모 4개, question_*.wav 음성 질문 2개 (16kHz 모노, 오프라인 TTS로 생성, KSS 기반 음성: 비상업 교육용)
- knowledge/base_knowledge.jsonl 기존 문서 지식 5건, sample_field_knowledge.jsonl 워크북 1 결과 예시 2건

## 검증 (2026-11-25)
- 노트북 4개를 위에서부터 순서대로 실행: 오류 없음 (STT는 같은 Whisper-small 가중치의 ONNX 판으로 대체 실행)
- Gradio 앱 두 개를 핸드폰 화면 크기(412px)로 버튼 순서대로 조작해 확인 (사진 인식→확정→음성 업로드→STT→저장 / 질문→답변 mp3)
- m4a·webm 녹음 → ffmpeg 16kHz WAV 변환 확인
- Colab 실제 GPU 실행, gradio.live 공유 주소, gTTS는 수업 전 강의자 계정에서 1회 확인 필요

## 폴더
- `tools/` 데이터·노트북·그림 생성 스크립트
- `figures/` Notion 강의자료 그림
- `legacy_webapp/` 이전 판(Windows 로컬 웹앱 + ESP32 LED) — 참고용
