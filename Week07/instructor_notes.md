# 7주차 강의자 노트

## 수업 전 준비 (10분)
1. 워크북 1·2를 Colab에서 열고 **0번 셀만 실행** → "다운로드 완료 … docs.google.com" 출력 확인
   - Drive 공유가 바뀌면 GitHub 백업으로 넘어갑니다. 두 경로 모두 실패하면 업로드 창이 뜹니다.
2. 수업용 OpenAI 키 확인 (6주차와 같은 30일 제한 키, 프로젝트 월 예산 한도 설정)
3. 워크북 2에서 키를 넣고 "RAG는 무엇의 약어인가요?" 1회 실행해 LLM 답변 확인

## PDF를 수정하려면
- Drive `7주_강의자료/week07_course_guide (실습용 PDF 원본)` Google 문서를 편집하면 학생 노트북이 자동으로 새 PDF를 받습니다.
- 페이지 구분은 각 제목의 "앞에 페이지 나누기" 설정입니다. 내용이 페이지를 넘기면 페이지 번호가 바뀌므로 `week07_faq.csv`의 `answer_page`도 함께 고쳐야 합니다.
- 수정 후 워크북 1 끝까지 실행해 임계값(`threshold`)이 0.16 근처인지 확인하고, 달라지면 워크북 2의 `THRESHOLD`를 바꿉니다.
- GitHub `data/` 백업 PDF도 Docs에서 PDF로 다운로드해 교체합니다.

## 코드 해설
| 코드 | 설명 | 학생이 자주 묻는 점 |
| --- | --- | --- |
| `page.extract_text()` | 문자 PDF에서 글자 추출 | `RAG 의`처럼 공백이 생기는 건 PDF 특성 |
| `re.sub(r"\s+", " ", text)` | 줄바꿈 정리 | 청크가 줄 단위로 끊기지 않게 함 |
| `chunk_words()` | 어절 단위 청크, 마지막 단어 도달 시 종료 | 원래 코드는 짧은 중복 꼬리 청크를 만들었음 |
| `TfidfVectorizer(analyzer="char_wb", ngram_range=(2,3), sublinear_tf=True)` | 어절 안 2~3글자 조각 | `word`로 바꾸면 Top-1이 0.538로 떨어짐 (워크북 1의 비교표) |
| `retrieve()` | 코사인 유사도 상위 k개 | `np.argsort(...)[::-1]`는 내림차순 |
| `evaluate()` | CSV로 Top-1/Top-3, 임계값 후보 계산 | Q03은 p.1에도 6주차 설명이 있어 1위를 놓침 → 토론 소재 |
| `THRESHOLD = 0.16` | 이 값 미만이면 "문서에서 확인할 수 없습니다" | LLM을 부르지 않아 비용도 절약 |
| `client.responses.create(..., instructions=, input=, temperature=0.2)` | 근거 기반 답변 | 키가 없으면 검색 모드 |
| `gr.Interface(..., flagging_mode="never")` | 질문·LLM 체크·top_k 슬라이더 → 답변·근거 | Gradio 5 이상 문법 |

## 시간 배분
- 1교시(50분): 노션 이론 정리 + 머메이드 구조도, 키워드 표
- 2교시(55분): 워크북 1 — 0~4절(30분), 설정 비교·그래프(15분), 기록표(10분)
- 3교시(55분): 워크북 2 — 검색기·프롬프트(15분), 키 연결(5분), Gradio(25분), 기록표(10분)
