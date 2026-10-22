# Week07 — PDF RAG 질의응답과 Gradio 웹 화면

PDF 텍스트 추출 → 청킹 → TF-IDF 문자 n-gram 검색 → 임계값 판정 → (선택) LLM 답변 → Gradio UI

## 실습 노트북 (Colab)
| 워크북 | 내용 | API 키 |
| --- | --- | --- |
| [워크북 1 — PDF 검색과 근거 표시](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week07/Week07_Workbook1_Student.ipynb) | 추출, 청킹, TF-IDF, 코사인 유사도, CSV 평가(Top-1/Top-3), 임계값 결정 | 불필요 |
| [워크북 2 — RAG 질의응답 + Gradio](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week07/Week07_Workbook2_Student.ipynb) | 임계값 판정, 프롬프트 구성, 선택형 LLM 답변, Gradio 화면 | 선택 |
| [예제실습](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week07/예제실습.ipynb) | 1교시 기초: 리스트·딕셔너리·튜플·세트, enumerate, 함수, TF-IDF, Gradio echo | 불필요 |

## 실습 데이터
노트북 0번 셀이 아래 순서로 자동 준비합니다. 학생이 직접 내려받을 필요가 없습니다.
1. Google Drive `7주_강의자료` 폴더 (링크가 있는 모든 사용자: 보기)
   - PDF 원본 Google 문서 `1WKmS8gV7-a4S1RjVifNo-dsLhN3bIdhyv4asO3B3qX8` → PDF로 내보내기
   - 평가 질문 CSV `1K_rzSWJhPd7skEyyh-3rK8SRMSknwMpS`
2. 이 저장소의 [`data/`](data) 백업 (같은 파일)
3. Colab 업로드 창

| 파일 | 설명 |
| --- | --- |
| `data/week07_course_guide.pdf` | 9쪽 실습 안내서 (RAG 구조, 추출, 청킹, TF-IDF, 임계값, 프롬프트, API 키, Gradio) |
| `data/week07_faq.csv` | 평가 질문 17개 — `answer_page`(정답 페이지), `in_document`(N이면 문서에 없는 질문) |

## 검증 결과 (2026-10-21, 기본값 size=60 / overlap=15 / char_wb (2,3))
- 두 노트북 전체 셀 실행 성공 (Jupyter 커널), 코드 줄 길이 79자 이하
- 청크 22개 · Top-1 정확도 0.923 · Top-3 정확도 1.0
- 문서에 있는 질문 최저 점수 0.201, 문서에 없는 질문 최고 점수 0.123 → 임계값 0.16
- Gradio 화면 실행 및 함수 호출 확인, LLM 경로는 가짜 클라이언트·연결 오류로 분기 확인
- 실제 OpenAI 호출과 Colab에서의 Drive 다운로드는 수업 전 1회 확인 필요

**주의:** API 키는 노트북·GitHub·노션에 적지 않습니다. 수업 시간에 따로 전달하고 Colab Secrets 또는 입력창(getpass)으로만 사용합니다.

## 이전 버전 보관
2026-10-21 오후의 '참고 PDF 3개 중 선택' 버전(워크북 1~3 학생용·완성본)은 [`archive_selected_pdf_20261021/`](archive_selected_pdf_20261021)에 보관했습니다.
