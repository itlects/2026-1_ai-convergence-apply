# Week06 — 생성형 AI 이해와 RAG 개념 (임베딩 · 유사도 · 질문 분류)

강의계획서 6주차 목표: **RAG를 이용한 분류모델을 설계하고, 임베딩 기반 유사도 계산 결과를 통해 질문을 사전 정의된 카테고리로 분류할 수 있다.**

## 수업 구성 (3시간)
| 교시 | 내용 | 자료 |
|---|---|---|
| 1교시 (50분) | 생성형 AI·LLM의 한계, 임베딩, 코사인 유사도, RAG 파이프라인, RAG 기반 분류 | Notion 강의자료 |
| 2교시 (55분) | **워크북 1 / Part 1** 임베딩과 유사도 검색 — 무료, API 키 불필요 | `Part1/` |
| 3교시 (55분) | **워크북 2 / Part 2** RAG 기반 질문 카테고리 분류 — OpenAI API (키 없으면 무료 모드) | `Part2/` |

## 파일
| Part | 버전 | 파일 | 바로 실행 |
|---|---|---|---|
| Part1 | 실습용 | [`Week06_Part1_Embedding_Similarity_실습용.ipynb`](Part1/Week06_Part1_Embedding_Similarity_%EC%8B%A4%EC%8A%B5%EC%9A%A9.ipynb) | [Colab에서 열기](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week06/Part1/Week06_Part1_Embedding_Similarity_%EC%8B%A4%EC%8A%B5%EC%9A%A9.ipynb) |
| Part1 | 완성본 | [`Week06_Part1_Embedding_Similarity_완성본.ipynb`](Part1/Week06_Part1_Embedding_Similarity_%EC%99%84%EC%84%B1%EB%B3%B8.ipynb) | [Colab에서 열기](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week06/Part1/Week06_Part1_Embedding_Similarity_%EC%99%84%EC%84%B1%EB%B3%B8.ipynb) |
| Part2 | 실습용 | [`Week06_Part2_RAG_Classification_실습용.ipynb`](Part2/Week06_Part2_RAG_Classification_%EC%8B%A4%EC%8A%B5%EC%9A%A9.ipynb) | [Colab에서 열기](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week06/Part2/Week06_Part2_RAG_Classification_%EC%8B%A4%EC%8A%B5%EC%9A%A9.ipynb) |
| Part2 | 완성본 | [`Week06_Part2_RAG_Classification_완성본.ipynb`](Part2/Week06_Part2_RAG_Classification_%EC%99%84%EC%84%B1%EB%B3%B8.ipynb) | [Colab에서 열기](https://colab.research.google.com/github/itlects/2026-1_ai-convergence-apply/blob/main/Week06/Part2/Week06_Part2_RAG_Classification_%EC%99%84%EC%84%B1%EB%B3%B8.ipynb) |

- **실습용**: `TODO` 셀을 학생이 직접 완성 / **완성본**: 정답 코드 (막힐 때 참고, 강의자 시연용)
- `requirements.txt`: Colab 밖(로컬)에서 실행할 때 필요한 패키지

## 실습 내용
**Part 1 — 임베딩과 유사도 검색 (무료)**
0. 환경 준비 (`jhgan/ko-sroberta-multitask` 한국어 임베딩 모델)
1. 문장 → 임베딩 벡터 2. 코사인 유사도 직접 계산 3. TF-IDF vs 임베딩 비교
4. 유사도 행렬 히트맵 5. 청킹(size/overlap) 6. 출처가 있는 검색 + 임계값 7. (도전) 나만의 문서 추가

**Part 2 — RAG 기반 질문 카테고리 분류**
0. Colab Secrets에 `OPENAI_API_KEY` 설정 (키가 없으면 무료 모델로 자동 전환)
1. 카테고리 지식베이스(수강·학사 / 장학·등록금 / 실습실·장비 / 취업·자격증)
2. 임베딩 함수(`text-embedding-3-small`) 3. top-k 검색 + 유사도 가중 투표로 분류, 임계값 미만은 '분류 불가'
4. 정확도·혼동표 평가 5. 임계값 비교 6. 검색 근거를 프롬프트에 넣어 LLM이 분류+이유 설명 (API 키 필요)

## 주의
- API 키는 Colab Secrets에만 저장하고 코드·스크린샷·GitHub·과제물에 넣지 않습니다.
- `CHAT_MODEL`(기본 `gpt-4o-mini`)은 노트북 첫 셀에서 바꿀 수 있습니다.
- 임계값(`threshold`)의 적절한 값은 임베딩 모델마다 다르므로 실습 중 직접 조정합니다.

다음 주(7주차): 오늘의 검색 → 근거 → 생성 구조에 PDF 로드와 Gradio UI를 붙여 RAG 챗봇을 완성합니다.
