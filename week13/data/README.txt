13주 실습 데이터 (인공지능융합활용, 교육용)
images/train/red, images/train/blue : 색 분류 학습 사진(합성, 640x480)
images/test : 시험 사진 (빨강, 그림자 진 빨강, 파랑, 초록, 흰색)
audio/voice_*.wav : 현장 음성 메모 4개 (16kHz, 모노, 16bit PCM)
audio/question_*.wav : 음성 질문 2개
audio/voice_reference.json : 각 음성의 원래 문장(정답 전사)
knowledge/base_knowledge.jsonl : 지난주 문서 RAG에서 만든 기존 지식 5건(가상 작업매뉴얼)
knowledge/sample_field_knowledge.jsonl : 워크북1 결과 예시 2건(본인 파일이 없을 때 사용)
음성은 오프라인 TTS(Mycroft mimic3 ko_KO kss_low 음성, KSS 데이터셋 CC BY-NC-SA 4.0)로 생성했으며 비상업 교육용으로만 사용합니다.
사진·지식 문장은 교육용으로 만든 가상 자료이며 개인정보가 없습니다.
