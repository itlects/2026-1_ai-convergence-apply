import json
from pathlib import Path

ROOT = Path(__file__).parent
def md(s):
    return dict(cell_type='markdown', metadata={}, source=s.splitlines(True))
def code(s):
    return dict(cell_type='code', metadata={}, source=s.splitlines(True), execution_count=None, outputs=[])

load = '''import json
from pathlib import Path
path = Path('sample_knowledge.jsonl')
if not path.exists():
    from google.colab import files
    files.upload()  # Drive에서 받은 sample_knowledge.jsonl 선택
records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
assert len(records) == 3
print('기본 지식:', len(records), '건')
for r in records:
    print(r['label'], r['text'], r['source'])'''
retrieve = '''def retrieve(question, rows):
    terms = question.lower().split()
    ranked = []
    for row in rows:
        if row.get('verified') is not True:
            continue
        text = (row['label'] + ' ' + row['text']).lower()
        score = sum(term in text for term in terms)
        if score:
            ranked.append((score, row))
    return [row for score, row in sorted(ranked, key=lambda x: -x[0])]

def answer(question, rows):
    hits = retrieve(question, rows)
    if not hits:
        return '관련 지식이 없습니다.'
    return '\\n'.join(f"[{row['source']}] {row['text']}" for row in hits)

print(answer('빨강', records))
print(answer('온도', records))
assert len(retrieve('빨강', records)) == 2
assert retrieve('온도', records) == []'''
add = '''new = {'id': 4, 'label': '파랑', 'text': '파랑 부품은 출고 전 무게를 확인한다.',
       'source': 'demo_record.wav', 'verified': True}
print('추가 전:', answer('무게', records))
updated = records + [new]
print('추가 후:', answer('무게', updated))
assert len(updated) == 4
assert len(retrieve('무게', updated)) == 1'''
export = '''out = Path('rag_knowledge.jsonl')
out.write_text('\\n'.join(json.dumps(r, ensure_ascii=False) for r in updated)+'\\n', encoding='utf-8')
assert len(out.read_text(encoding='utf-8').splitlines()) == len(updated)
print('저장:', out, len(updated), '건')'''
student_add = '''# WB1에서 저장한 field_knowledge.jsonl이 있으면 업로드 후 사용합니다.
# 아직 없으면 아래 연습 문장을 자신의 관찰 내용으로 바꾸세요.
p = Path('field_knowledge.jsonl')
if p.exists():
    added = [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert added and all(r.get('verified') is True and r.get('text') for r in added)
else:
    added = [{'id': 1, 'label': '파랑', 'text': '파랑 부품은 출고 전 무게를 확인한다.', 'source': 'practice_text', 'verified': True}]
for i, r in enumerate(added, start=4):
    r['id'] = i
updated = records + added
print('추가 전:', len(records), '추가 후:', len(updated))
print(answer('무게', records))
print(answer('무게', updated))
assert len(updated) == len(records) + len(added)'''

speech = '''import wave
from IPython.display import Audio, display
p = Path('sample_1.wav')
if not p.exists():
    from google.colab import files
    files.upload()  # Drive에서 받은 sample_1.wav 선택
with wave.open(str(p), 'rb') as w:
    print('채널:', w.getnchannels(), '샘플링:', w.getframerate(), '길이:', round(w.getnframes()/w.getframerate(), 2), '초')
display(Audio(filename=str(p)))
print('참조 문장:', records[0]['reference_en'])'''
for role in ['student','teacher']:
    cells = [md('# 13주 Workbook 2 — '+ ('학생 실습' if role=='student' else '강의자 시연')+'\nCPU 실습 · 데이터는 Drive에서 미리 다운로드. 첫 셀부터 차례로 실행.'),md('## 1. 준비된 지식 3건 열기\n`sample_knowledge.jsonl`을 업로드합니다. JSONL은 한 줄에 한 JSON 객체입니다.'),code(load),md('## 2. WAV 파일 재생\n영어 합성 음성 예제입니다. 참조 문장은 이미 제공된 정답이며 자동 STT 출력이 아닙니다. WB1에서 실제 음성인식을 실행합니다.'),code(speech),md('## 3. 기존 지식으로 검색\n키워드 일치 점수로 근거를 가져오는 간단한 RAG형 검색입니다. LLM 생성이 아니라 근거 문장을 그대로 반환합니다.'),code(retrieve),md('## 4. 새 지식 추가\n학생은 좌측 파일 메뉴로 WB1의 JSONL을 업로드하거나 예제 문장을 수정합니다.'),code(student_add if role=='student' else add),md('## 5. JSONL 내보내기\n왼쪽 파일 창에서 rag_knowledge.jsonl 다운로드.'),code(export),md('## 6. 결과 기록\n- 기존 빨강 검색 건수: __\n- 지식 추가 전/후 건수: __ / __\n- 내가 검색한 질문 및 출처: __\n- 오인식 교정 방법: __' if role=='student' else '## 6. 시연 해설\n기본 3건, 빨강 2건, 온도 0건, 무게 0→1건. 가중치를 변경해도 데이터가 없으면 답하지 않아야 한다.')]
    nb = dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},nbformat=4,nbformat_minor=5)
    (ROOT/f'WB2_{role}.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=2),encoding='utf-8')
