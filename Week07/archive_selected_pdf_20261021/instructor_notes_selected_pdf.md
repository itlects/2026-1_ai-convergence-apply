# 강의자 코드 해설

- `PdfReader`: PDF 문서 열기. `extract_text()`는 문자 PDF에서만 동작하며 OCR은 별도 처리해야 함.
- `chunk_words(text,size,overlap)`: 단어 구간 분할, 청크 크기와 겹침을 조정하는 함수.
- `TfidfVectorizer(analyzer='char', ngram_range=(2,4))`: 한글 문자 조각으로 TF-IDF 생성, 의미 임베딩과 구분.
- `fit_transform()`: 문서 사전과 벡터 생성. `transform()`: 질문에 같은 사전 적용.
- `cosine_similarity()`: 문서와 질문의 코사인 유사도.
- `np.argsort(scores)[::-1]`: 유사도 높은 순서로 정렬.
- `userdata.get('OPENAI_API_KEY')`: Colab Secrets에서 키 읽기.
- `OpenAI().responses.create()`: 선택적으로 검색된 근거를 LLM 입력으로 전송.
- `gr.Interface()`, `gr.Textbox()`, `gr.Checkbox()`, `app.launch()`: Gradio UI 요소.

## 검증 요약
- 2개 노트북의 코드 셀 정적 파이썬 AST 파싱 통과.
- 제공 PDF 실물에서 텍스트 추출 성공: 2페이지 / 청크 5개 / TF-IDF 행렬 (5,1988).
- RAG, API 키 관리, 청킹 질문 3개 검색 실행 성공.
- API 호출은 실제 비용 및 키가 필요하므로 수행하지 않았고, Gradio UI의 브라우저 렌더링도 Colab에서는 최종 확인 필요.

## 수업 진행
1. PDF를 다운로드해 Colab에 직접 업로드.
2. 1번 노트북에서 3개 질문 결과와 청크 설정 전후 차이를 작성.
3. 2번 노트북에서 무료 UI 모드를 기본 실행. API 키가 있는 학습자만 LLM 모드를 선택.
