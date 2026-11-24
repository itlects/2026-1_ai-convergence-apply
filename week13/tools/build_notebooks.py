"""13주 Colab 노트북 4개 생성: WB1/WB2 × 학생용/강의자용.

셀 표기: ('md'|'code', 대상, 내용)  대상: 'all' | 'student' | 'teacher'
"""
import sys
from pathlib import Path

import nbformat as nbf

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
DATA_ID = sys.argv[2] if len(sys.argv) > 2 else 'DRIVE_FILE_ID'
REPO = 'itlects/2026-1_ai-convergence-apply'
BACKUP = f'https://raw.githubusercontent.com/{REPO}/main/week13/data/week13_data.zip'

SETUP_INSTALL = '''# 0-1. 필요한 도구 설치 (약 30초, 처음 한 번만)
%pip install -q "gradio>=5,<7" gTTS qrcode'''

SETUP_DATA = f'''# 0-2. 실습 데이터 내려받기: Google Drive → Colab (약 5초)
import os
import zipfile
import urllib.request

DATA_ID = '{DATA_ID}'
BACKUP_URL = ('{BACKUP}')


def get_data():
    if os.path.isdir('week13_data'):
        return 'already'
    try:
        import gdown
        gdown.download(id=DATA_ID, output='week13_data.zip',
                       quiet=True)
        zipfile.ZipFile('week13_data.zip').extractall('.')
        return 'drive'
    except Exception as e:
        print('Drive 다운로드 실패 → GitHub 예비 주소 사용:', e)
        urllib.request.urlretrieve(BACKUP_URL, 'week13_data.zip')
        zipfile.ZipFile('week13_data.zip').extractall('.')
        return 'github'


print('받은 곳:', get_data())
for root, dirs, names in sorted(os.walk('week13_data')):
    if names:
        print(root, '→', len(names), '개 파일')'''

STT_LOAD = '''# 음성인식(STT) 모델 불러오기: OpenAI Whisper-small
# 처음 실행 시 모델(약 1GB)을 내려받는다. GPU 약 30초, CPU 약 1~2분.
import torch
from transformers import pipeline

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
stt = pipeline(
    'automatic-speech-recognition',
    model='openai/whisper-small',
    device=DEVICE,
)
print('STT 준비 완료, 사용 장치:', DEVICE)'''

AUDIO_UTILS = '''# 음성 도구 함수: 변환(ffmpeg) · 읽기(wave) · 텍스트 변환(STT)
import subprocess
import wave
import numpy as np
from IPython.display import Audio, display


def to_wav16k(src, dst):
    """어떤 녹음 파일(m4a, mp3, webm, wav)이든 16kHz·모노·16bit WAV로 바꾼다."""
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src),
         '-ac', '1', '-ar', '16000', '-sample_fmt', 's16', str(dst)],
        check=True,
    )
    return str(dst)


def read_wav(path):
    """WAV 파일 → (샘플 배열 -1~1, 샘플링레이트)"""
    with wave.open(str(path), 'rb') as w:
        sr = w.getframerate()
        pcm = w.readframes(w.getnframes())
    x = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768
    return x, sr


def speech_to_text(path):
    """WAV → 한국어 텍스트"""
    x, sr = read_wav(path)
    out = stt({'raw': x, 'sampling_rate': sr},
              generate_kwargs={'language': 'korean',
                               'task': 'transcribe'})
    return out['text'].strip()


# STT가 자주 틀리는 현장 용어를 바로잡는 교정 사전 (틀린 말 → 바른 말)
FIX = {
    '바람 부품': '파랑 부품',
    '하랑 부품': '파랑 부품',
    '파란 부품': '파랑 부품',
    '빨간 부품': '빨강 부품',
    '부풍': '부품',
}


def fix_terms(text):
    for wrong, right in FIX.items():
        text = text.replace(wrong, right)
    return text'''

TTS_UTIL = '''# 텍스트 → 음성(TTS): Google TTS(gTTS)로 mp3 만들기
def text_to_speech(text, path='answer.mp3'):
    try:
        from gtts import gTTS
        gTTS(text, lang='ko').save(path)
        return path
    except Exception as e:
        print('TTS 실패(인터넷 확인):', e)
        return None'''

QR_UTIL = '''# 공유 주소를 QR 코드로 보여 주는 함수 (핸드폰 카메라로 스캔)
import qrcode
from IPython.display import Image as ShowImage


def show_qr(url):
    if not url:
        print('공유 주소가 없습니다. 위 출력의 오류를 확인하세요.')
        return
    qrcode.make(url).save('share_qr.png')
    print('핸드폰으로 접속:', url)
    display(ShowImage('share_qr.png', width=220))'''


def T(note):
    return ('md', 'teacher', '> 👩‍🏫 **강의자 메모** — ' + note)


def S(note):
    return ('md', 'student', '> ✍️ **학생 기록** — ' + note)


# ---------------------------------------------------------------- WB1
WB1 = [
    ('md', 'student', '''# 13주 워크북 1 (학생용) — 음성 라벨링 카운터
**카메라 인식 → 카운터·LED → 녹음 → 음성→텍스트 → 현장 지식 저장**

이 노트북은 GitHub에서 열린 **학생용 사본**입니다. 먼저 `파일 → Drive에 사본 저장`을 누르세요.
강의자 화면의 실행 결과와는 완전히 분리되어 있습니다.

| 순서 | 할 일 | 확인 결과 |
|---|---|---|
| 0 | 준비: 런타임·데이터 | 데이터 폴더 4개 |
| 1 | 카메라 인식 학습(색 분류) | 시험 사진 5장 결과 |
| 2 | 카운터 + LED | 확정 시 LED ON |
| 3 | 녹음 파일(WAV) 확인·재생 | 길이·소리 |
| 4 | 음성→텍스트(STT)·교정 | 교정 문장 |
| 5 | 파이프라인 통합·지식 저장 | field_knowledge.jsonl 2줄 |
| 6 | **핸드폰 앱**으로 직접 실습 | 내 사진·내 목소리 기록 |
| 7 | 결과 저장·보고 | 결과보고 페이지 작성 |

✍️ 표시는 **결과보고 페이지**에 옮겨 적을 내용입니다.'''),
    ('md', 'teacher', '''# 13주 워크북 1 (강의자용 시연) — 음성 라벨링 카운터
학생용과 **별도 파일**입니다. 이 노트북의 실행 결과는 학생 노트북에 영향을 주지 않습니다.
👩‍🏫 강의자 메모에는 설명 포인트와 예상 결과가 있습니다.

| 순서 | 할 일 | 예상 결과 |
|---|---|---|
| 0 | 준비 | 폴더 4개 |
| 1 | 색 분류 학습 | 빨강·빨강·파랑·미확정·미확정 |
| 2 | 카운터·LED | 확정 시 ON |
| 3 | WAV | 16000Hz·모노·약 3~4초 |
| 4 | STT·교정 | 오인식 → 교정 |
| 5 | 통합·저장 | 2줄 |
| 6 | 핸드폰 앱 시연 | QR 접속 |'''),
    ('md', 'all', '''## 0. 준비
1. 메뉴 `런타임 → 런타임 유형 변경 → T4 GPU` (없으면 CPU도 동작, STT가 느릴 뿐)
2. 아래 셀을 **위에서부터 차례로** 실행(▶ 또는 Shift+Enter)'''),
    ('code', 'all', SETUP_INSTALL),
    ('code', 'all', SETUP_DATA),
    T('폴더 4개(images/train/red, blue, images/test, audio, knowledge) 출력 확인. Drive 다운로드가 몰려 실패하면 자동으로 GitHub 예비 주소를 사용한다.'),
    ('md', 'all', '''## 1. 카메라 인식 학습 — 색으로 부품 분류하기
**생각해 보기:** 사람은 어떻게 빨강 부품을 알아볼까? 컴퓨터는 사진을 **숫자(R, G, B)** 로 본다.

학습 방법(최근접 중심, Nearest Centroid)
1. 학습 사진마다 **가운데 영역의 평균 RGB**를 구한다 → 특징(feature)
2. 같은 라벨끼리 평균 → **클래스 중심(centroid)** = 학습 결과(모델)
3. 새 사진은 **가장 가까운 중심**의 라벨로 예측, 너무 멀면 `미확정`'''),
    ('code', 'all', '''# 1-1. 학습 사진 보기
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

DATA = Path('week13_data')
KOR = {'red': '빨강', 'blue': '파랑'}

train_files = {
    d.name: sorted(d.glob('*.jpg'))
    for d in sorted((DATA / 'images' / 'train').iterdir())
}
fig, axes = plt.subplots(2, 5, figsize=(12, 4))
for row, (label, files) in enumerate(train_files.items()):
    for col, path in enumerate(files):
        axes[row, col].imshow(Image.open(path))
        axes[row, col].set_title(path.name, fontsize=8)
        axes[row, col].axis('off')
plt.tight_layout()
plt.show()'''),
    ('code', 'all', '''# 1-2. 특징 추출: 사진 가운데 40% 영역의 평균 RGB
def center_rgb(img):
    a = np.asarray(img.convert('RGB'), dtype=float)
    h, w, _ = a.shape
    roi = a[int(h * 0.3):int(h * 0.7), int(w * 0.3):int(w * 0.7)]
    return roi.reshape(-1, 3).mean(axis=0)


for label, files in train_files.items():
    for path in files:
        r, g, b = center_rgb(Image.open(path))
        print(f'{label:5s} {path.name}: R={r:5.0f} G={g:5.0f} B={b:5.0f}')'''),
    ('code', 'all', '''# 1-3. 학습: 라벨별 평균 RGB = 클래스 중심
features = {
    label: np.array([center_rgb(Image.open(p)) for p in files])
    for label, files in train_files.items()
}
centroids = {label: f.mean(axis=0) for label, f in features.items()}
for label, c in centroids.items():
    print(KOR[label], '중심 RGB =', c.round())

# 그림: R(가로)–B(세로) 평면에 학습 사진(점)과 중심(별)
plt.figure(figsize=(5, 4))
for label, f in features.items():
    plt.scatter(f[:, 0], f[:, 2], color=label, label=label)
    c = centroids[label]
    plt.scatter(c[0], c[2], color=label, marker='*', s=300,
                edgecolor='black')
plt.xlabel('R (red)')
plt.ylabel('B (blue)')
plt.xlim(0, 255)
plt.ylim(0, 255)
plt.legend()
plt.title('Training data and centroids')
plt.show()'''),
    T('“학습 = 데이터로부터 모델(여기서는 중심값 2개)을 계산하는 과정”을 강조. 빨강 중심 약 (190,43,49), 파랑 약 (40,68,185).'),
    ('code', 'all', '''# 1-4. 예측: 가장 가까운 중심 찾기 (거리 = 유클리드 거리)
UNSURE_DIST = 100   # 이 거리 이상이면 '미확정'


def classify(img):
    rgb = center_rgb(img)
    dists = {
        label: float(np.linalg.norm(rgb - c))
        for label, c in centroids.items()
    }
    best = min(dists, key=dists.get)
    if dists[best] >= UNSURE_DIST:
        return '미확정', dists[best]
    return KOR[best], dists[best]


test_files = sorted((DATA / 'images' / 'test').glob('*.jpg'))
fig, axes = plt.subplots(1, len(test_files), figsize=(14, 3))
for ax, path in zip(axes, test_files):
    label, dist = classify(Image.open(path))
    print(f'{path.name:22s} → {label} (거리 {dist:.0f})')
    ax.imshow(Image.open(path))
    ax.set_title(f'{path.stem}\\ndist={dist:.0f}', fontsize=8)
    ax.axis('off')
plt.show()'''),
    T('예상: blue_01→파랑(약 5), green_01→미확정(약 145), red_01→빨강(약 2), red_shadow→빨강(약 75), white_01→미확정(약 238). 거리는 확률이 아니라 “얼마나 다른가”의 크기임을 설명.'),
    S('시험 사진 5장의 예측 라벨과 거리를 결과보고 **표 1**에 적는다. `UNSURE_DIST`를 60으로 바꿔 다시 실행하면 어떤 사진의 결과가 달라지는지도 적는다(실험 후 100으로 되돌린다).'),
    ('md', 'all', '''## 2. 카운터와 LED — “확정” 이벤트
카메라는 1초에 여러 장을 보므로 **예측할 때마다 세면 안 된다.** 사람이 `확정`을 누를 때만 1건 증가하고 LED가 켜진다.
LED가 켜져 있으면 “음성 기록을 기다리는 중”이라는 뜻이다. 지식을 저장하면 LED가 꺼진다.'''),
    ('code', 'all', '''# 2-1. 카운터 · 가상 LED
from IPython.display import HTML

counter = {'빨강': 0, '파랑': 0}
state = {'led': False, 'label': None}


def led_html(on):
    color = '#22c55e' if on else '#9ca3af'
    text = 'LED ON (음성 기록 대기)' if on else 'LED OFF'
    return (f"<span style='display:inline-block;width:22px;height:22px;"
            f"border-radius:50%;background:{color};"
            f"vertical-align:middle'></span> <b>{text}</b>")


def confirm(label):
    """확정: 카운터 +1, LED ON"""
    if label not in counter:
        print('미확정 결과는 확정할 수 없습니다.')
        return False
    counter[label] += 1
    state['led'] = True
    state['label'] = label
    return True


label, dist = classify(Image.open(DATA / 'images/test/test_red_01.jpg'))
confirm(label)
print('카운터:', counter)
display(HTML(led_html(state['led'])))'''),
    ('code', 'all', '''# 2-2. 미확정은 세지 않는다
label, dist = classify(Image.open(DATA / 'images/test/test_green_01.jpg'))
print('예측:', label)
confirm(label)
print('카운터:', counter)'''),
    ('md', 'all', '''## 3. 녹음 파일(WAV) 확인과 재생
WAV = **헤더**(샘플링레이트·채널·비트) + **PCM 샘플**(소리 크기를 일정 간격으로 잰 숫자).
길이(초) = 샘플 수 ÷ 샘플링레이트. Whisper는 **16kHz·모노** 음성을 사용한다.'''),
    ('code', 'all', AUDIO_UTILS),
    ('code', 'all', '''# 3-1. 현장 음성 메모 정보 보기 · 파형 · 재생
AUDIO = DATA / 'audio'
wav_path = AUDIO / 'voice_red_01.wav'
with wave.open(str(wav_path), 'rb') as w:
    print('채널 수   :', w.getnchannels())
    print('샘플링레이트:', w.getframerate(), 'Hz')
    print('샘플 수   :', w.getnframes())
    print('길이      :', round(w.getnframes() / w.getframerate(), 2), '초')

x, sr = read_wav(wav_path)
plt.figure(figsize=(10, 2))
plt.plot(np.arange(len(x)) / sr, x)
plt.xlabel('time (s)')
plt.title('voice_red_01.wav waveform')
plt.show()
display(Audio(filename=str(wav_path)))'''),
    ('md', 'all', '''### 3-2. (선택) 내 핸드폰 녹음 파일 올리기
핸드폰 녹음 앱으로 “빨강 부품은 …에 보관합니다”처럼 한 문장을 녹음한다.
파일을 PC로 옮기기 어렵다면 **6단계 핸드폰 앱**에서 바로 녹음해도 된다.
올리려면 아래 셀의 `USE_MY_RECORDING = True`로 바꾸고 실행 → 파일 선택.'''),
    ('code', 'all', '''# 3-2. 핸드폰 녹음(m4a 등) → 16kHz WAV 변환
USE_MY_RECORDING = False   # True로 바꾸면 업로드 창이 열린다

if USE_MY_RECORDING:
    from google.colab import files
    uploaded = files.upload()
    src = list(uploaded)[0]
    my_wav = to_wav16k(src, 'my_record_1.wav')
    print('변환 완료:', my_wav)
    display(Audio(filename=my_wav))
else:
    print('건너뜀 (기본 음성 파일로 계속)')'''),
    ('md', 'all', '''## 4. 음성 → 텍스트(STT)와 교정
1. Whisper 모델로 WAV를 텍스트로 바꾼다.
2. 정답 문장과 비교해 **틀린 글자 비율(CER)** 을 본다.
3. 현장 용어 **교정 사전(FIX)** 을 적용하고, 마지막은 **사람이 듣고 확인**한다.'''),
    ('code', 'all', STT_LOAD),
    ('code', 'all', '''# 4-1. 현장 음성 4개 → 텍스트
import json

reference = json.loads(
    (AUDIO / 'voice_reference.json').read_text(encoding='utf-8'))


def cer(ref, hyp):
    """글자 오류율: 편집거리 ÷ 정답 글자 수 (공백 제외)"""
    r, h = ref.replace(' ', ''), hyp.replace(' ', '')
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1,
                      prev + (r[i - 1] != h[j - 1]))
            prev, d[j] = d[j], cur
    return d[len(h)] / max(len(r), 1)


stt_results = {}
for name in ['voice_red_01.wav', 'voice_blue_01.wav',
             'voice_red_02.wav', 'voice_blue_02.wav']:
    raw = speech_to_text(AUDIO / name)
    fixed = fix_terms(raw)
    stt_results[name] = (raw, fixed)
    print(name)
    print('  정답 :', reference[name])
    print('  STT  :', raw, f'(CER {cer(reference[name], raw):.2f})')
    print('  교정 :', fixed, f'(CER {cer(reference[name], fixed):.2f})')'''),
    T('합성 음성이라 “파랑→바람/하랑”, “검사 후 왼쪽→건사분은쪽” 같은 오인식이 생길 수 있다(실행마다·장치마다 다를 수 있음). 교정 사전은 용어만 고치므로, 마지막 확인은 사람이 한다는 점(Human-in-the-loop)을 강조.'),
    S('음성 2개 이상의 STT 결과·교정 결과·CER을 결과보고 **표 2**에 적는다.'),
    ('md', 'all', '''## 5. 파이프라인 통합: 카메라 → LED → 녹음 → STT → 지식 저장
지식 1건(JSON 객체) = `라벨 + 교정 문장 + STT 원문 + 출처 WAV + 검증 여부 + 시각`.
JSONL = **한 줄에 JSON 하나**. 줄을 추가하면 지식이 늘어난다.'''),
    ('code', 'all', '''# 5-1. 지식 레코드 만들기 · JSONL 저장 함수
from datetime import datetime

knowledge = []


def make_record(label, text, stt_raw, source):
    return {
        'id': f'voice-{len(knowledge) + 1:03d}',
        'label': label,
        'count': counter.get(label, 0),
        'text': text,
        'stt_raw': stt_raw,
        'source': source,
        'type': 'voice_note',
        'verified': True,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }


def save_jsonl(rows, path):
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    Path(path).write_text('\\n'.join(lines) + '\\n', encoding='utf-8')
    return path'''),
    ('code', 'all', '''# 5-2. 통합 파이프라인 함수
def pipeline_once(image_path, wav_path, reviewed_text=None):
    # ① 카메라 인식
    label, dist = classify(Image.open(image_path))
    print(f'① 인식: {label} (거리 {dist:.0f})')
    # ② 확정 → 카운터 +1, LED ON
    if not confirm(label):
        return None
    print('② 카운터:', counter, '| LED ON')
    # ③ 녹음 파일 재생
    display(Audio(filename=str(wav_path)))
    # ④ STT + 용어 교정 (+ 사람 확인 문장이 있으면 그것을 사용)
    raw = speech_to_text(wav_path)
    text = reviewed_text or fix_terms(raw)
    print('④ STT :', raw)
    print('   확정 문장:', text)
    # ⑤ 지식 저장 → LED OFF
    knowledge.append(make_record(label, text, raw, Path(wav_path).name))
    save_jsonl(knowledge, 'field_knowledge.jsonl')
    state['led'] = False
    print('⑤ 저장 완료, 지식', len(knowledge), '건 | LED OFF')
    return knowledge[-1]'''),
    ('code', 'all', '''# 5-3. 1건째: 빨강 부품 (사람이 듣고 확인한 문장을 넣는다)
pipeline_once(
    DATA / 'images/test/test_red_01.jpg',
    AUDIO / 'voice_red_01.wav',
    reviewed_text='빨강 부품은 검사 후 왼쪽 상자에 보관합니다.',
)'''),
    ('code', 'student', '''# 5-4. 2건째: 파랑 부품
# ✍️ 음성을 듣고 바른 문장을 직접 입력해 보자. (비워 두면 교정 사전 결과 사용)
MY_REVIEWED_TEXT = ''

pipeline_once(
    DATA / 'images/test/test_blue_01.jpg',
    AUDIO / 'voice_blue_01.wav',
    reviewed_text=MY_REVIEWED_TEXT or None,
)'''),
    ('code', 'teacher', '''# 5-4. 2건째: 파랑 부품
pipeline_once(
    DATA / 'images/test/test_blue_01.jpg',
    AUDIO / 'voice_blue_01.wav',
    reviewed_text='파랑 부품은 습기에 약하니 뚜껑을 닫아 보관합니다.',
)'''),
    ('code', 'all', '''# 5-5. 저장된 JSONL 확인 (2줄)
print(Path('field_knowledge.jsonl').read_text(encoding='utf-8'))
print('카운터:', counter)'''),
    T('5-3·5-4 실행 후 2줄이 보이면 성공. 2-1에서 이미 1회 확정했기 때문에 카운터는 빨강 2, 파랑 1이 된다. “count”는 확정 시점의 누적 건수다.'),
    ('md', 'all', '''## 6. 핸드폰으로 실습하기 — 음성 라벨링 앱
아래 셀을 실행하면 **QR 코드**와 `https://….gradio.live` 주소가 나온다.
핸드폰 카메라로 QR을 찍어 접속 → 마이크·카메라 권한 허용.

| 순서 | 핸드폰 화면 | 결과 |
|---|---|---|
| ① | 사진: 📷 촬영(또는 앨범) → `1. 인식` | 라벨·거리 |
| ② | `2. 확정` | 카운터 +1, LED ON |
| ③ | 녹음: 🎙️ 녹음 → 정지 → `3. 음성→텍스트` | WAV 재생, STT 문장 |
| ④ | 문장 확인·수정 → `4. 지식 저장` | 표에 1줄 추가, LED OFF |
| ⑤ | 파일 받기 | field_knowledge.jsonl |

빨강·파랑 물체(색종이, 물병 뚜껑 등)를 화면 가운데에 크게 찍는다. 주변에 사람이 나오거나 개인정보를 말하지 않는다.'''),
    ('code', 'all', QR_UTIL),
    ('code', 'all', '''# 6-1. 핸드폰용 음성 라벨링 앱 (Gradio)
import gradio as gr

app_last = {'label': None, 'raw': ''}


def ui_status():
    return (led_html(state['led'])
            + f"&nbsp;&nbsp; 빨강 <b>{counter['빨강']}</b>"
            + f" · 파랑 <b>{counter['파랑']}</b>")


def ui_classify(img):
    if img is None:
        return '사진을 먼저 찍으세요.', ui_status()
    label, dist = classify(img)
    app_last['label'] = label
    return f'{label} (거리 {dist:.0f})', ui_status()


def ui_confirm():
    if not confirm(app_last['label']):
        return '미확정·사진 없음은 확정할 수 없습니다.', ui_status()
    return f"{app_last['label']} 확정", ui_status()


def ui_stt(audio_path):
    if audio_path is None:
        return None, '', '녹음을 먼저 하세요.'
    n = len(knowledge) + 1
    wav = to_wav16k(audio_path, f'phone_record_{n}.wav')
    raw = speech_to_text(wav)
    app_last['raw'] = raw
    app_last['wav'] = wav
    return wav, fix_terms(raw), f'STT 원문: {raw}'


def ui_save(text):
    if not state['led']:
        return '먼저 2. 확정을 누르세요.', ui_status(), None, None
    if not app_last.get('wav') or not text.strip():
        return '3. 음성→텍스트를 먼저 하세요.', ui_status(), None, None
    knowledge.append(make_record(state['label'], text.strip(),
                                 app_last['raw'],
                                 Path(app_last['wav']).name))
    save_jsonl(knowledge, 'field_knowledge.jsonl')
    state['led'] = False
    app_last['wav'] = None
    rows = [[r['id'], r['label'], r['text'], r['source']]
            for r in knowledge]
    return (f'저장 완료 (총 {len(knowledge)}건)', ui_status(), rows,
            'field_knowledge.jsonl')


with gr.Blocks(title='13주 음성 라벨링 카운터') as demo:
    gr.Markdown('## 🎙️ 음성 라벨링 카운터')
    status = gr.HTML(ui_status())
    photo = gr.Image(type='pil', sources=['upload', 'webcam'],
                     label='① 사진 (가운데에 크게)')
    with gr.Row():
        b_cls = gr.Button('1. 인식', variant='primary')
        b_ok = gr.Button('2. 확정 (LED ON)')
    result = gr.Textbox(label='인식 결과')
    voice = gr.Audio(sources=['microphone', 'upload'], type='filepath',
                     label='② 녹음 (한 문장)')
    b_stt = gr.Button('3. 음성→텍스트', variant='primary')
    play = gr.Audio(label='변환된 WAV 재생', type='filepath')
    raw_box = gr.Markdown()
    text = gr.Textbox(label='③ 문장 확인·수정 후 저장', lines=2)
    b_save = gr.Button('4. 지식 저장 (LED OFF)', variant='primary')
    msg = gr.Markdown()
    table = gr.Dataframe(headers=['id', '라벨', '문장', '출처'],
                         label='저장된 현장 지식')
    file_out = gr.File(label='field_knowledge.jsonl 받기')

    b_cls.click(ui_classify, photo, [result, status])
    b_ok.click(ui_confirm, None, [result, status])
    b_stt.click(ui_stt, voice, [play, text, raw_box])
    b_save.click(ui_save, text, [msg, status, table, file_out])

demo.launch(share=True)
show_qr(demo.share_url)'''),
    T('학생 핸드폰마다 각자 Colab의 주소가 생긴다(서로 섞이지 않음). 주소는 Colab 실행 중에만 동작. 권한 거부 시 브라우저 주소창의 자물쇠 → 권한 허용. 카메라 미리보기가 안 되면 “업로드”로 촬영.'),
    S('핸드폰 앱에서 저장한 내 지식 2건(라벨·문장·STT 원문)을 결과보고 **표 3**에 적고, 앱 화면 캡처 1장을 붙인다.'),
    ('md', 'all', '''## 7. 결과 저장
`field_knowledge.jsonl`을 내려받아 워크북 2에서 사용한다. (Colab을 닫으면 파일이 사라진다)'''),
    ('code', 'all', '''# 7-1. 결과 파일 내려받기
print('지식', len(knowledge), '건, 카운터', counter)
try:
    from google.colab import files
    files.download('field_knowledge.jsonl')
except ImportError:
    print('Colab이 아닌 환경: 파일은 현재 폴더에 있습니다.')'''),
    S('결과보고 **요약**: ① 학습과 예측의 차이 ② 확정 버튼이 필요한 이유 ③ STT가 틀린 단어와 교정 방법을 각각 1문장으로 적는다.'),
    ('md', 'teacher', '''### 👩‍🏫 정리 질문
1. 중심값(centroid)은 언제 계산되나? → 학습 단계(1-3), 예측은 계산된 중심을 사용
2. 같은 물체가 계속 보이는데 카운터가 한 번만 증가하는 이유? → 확정 이벤트에서만 증가
3. STT 결과를 그대로 저장하면 생기는 문제? → 틀린 지식이 검색됨 → 교정·검증 필요'''),
]

# ---------------------------------------------------------------- WB2
WB2 = [
    ('md', 'student', '''# 13주 워크북 2 (학생용) — 음성으로 추가 지식베이스 만들기와 음성 챗봇
**기존 문서 지식 + 현장 음성 지식 → 검색(RAG) 비교 → 마이크로 묻고 스피커로 듣기**

`파일 → Drive에 사본 저장` 후 실행한다. 강의자 노트북과 분리된 학생용 사본이다.

| 순서 | 할 일 | 확인 결과 |
|---|---|---|
| 0 | 준비 | 데이터·STT |
| 1 | 기존 지식(지난주 문서 RAG) | 5건 |
| 2 | 음성 → 추가 지식 만들기 | 전사·교정·검토 |
| 3 | 품질 점검·병합 | rag_knowledge.jsonl |
| 4 | 검색 전/후 비교 | 비교표 |
| 5 | 음성 질문 → 답변 음성 | mp3 재생 |
| 6 | **핸드폰 음성 챗봇** | 묻고 듣기 |
| 7 | 결과 저장·보고 | 결과보고 페이지 |'''),
    ('md', 'teacher', '''# 13주 워크북 2 (강의자용 시연) — 추가 지식베이스와 음성 챗봇
학생용과 별도 파일. 예상 결과와 설명 포인트는 👩‍🏫 메모에 있다.

| 단계 | 예상 |
|---|---|
| 1 | 기존 5건 |
| 2~3 | 검증 지식 9건(기존 5 + 음성 4) |
| 4 | “빨강 보관” 질문: 전 A라인 조립(질문과 안 맞음) → 후 왼쪽 상자 |
| 5 | 답변 mp3 재생 |'''),
    ('md', 'all', '''## 0. 준비
`런타임 → 런타임 유형 변경 → T4 GPU`(없으면 CPU) 후 차례로 실행.'''),
    ('code', 'all', SETUP_INSTALL),
    ('code', 'all', SETUP_DATA),
    ('code', 'all', AUDIO_UTILS),
    ('code', 'all', STT_LOAD),
    ('code', 'all', TTS_UTIL),
    ('md', 'all', '''## 1. 기존 지식 불러오기
지난주 문서 RAG에서 만든 **문서 조각(청크)** 5건이다. 작업 매뉴얼에는 “어디에 보관하는지”가 없다.'''),
    ('code', 'all', '''# 1-1. JSONL 읽기
import json
from pathlib import Path
import pandas as pd

DATA = Path('week13_data')
AUDIO = DATA / 'audio'


def load_jsonl(path):
    text = Path(path).read_text(encoding='utf-8')
    return [json.loads(line) for line in text.splitlines()
            if line.strip()]


def save_jsonl(rows, path):
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    Path(path).write_text('\\n'.join(lines) + '\\n', encoding='utf-8')


base = load_jsonl(DATA / 'knowledge/base_knowledge.jsonl')
print('기존 지식', len(base), '건')
pd.DataFrame(base)[['id', 'label', 'text', 'source']]'''),
    ('md', 'all', '''## 2. 음성 → 추가 지식 만들기
추가 지식 생성 5단계: **수집(녹음) → 전사(STT) → 교정(용어 사전) → 구조화(JSON) → 검증(사람 확인)**

### 2-1. 워크북 1 결과 가져오기
워크북 1의 `field_knowledge.jsonl`이 있으면 `USE_MY_FILE = True`로 바꾸고 업로드한다. 없으면 예시 파일을 사용한다.'''),
    ('code', 'all', '''# 2-1. 워크북 1 현장 지식
USE_MY_FILE = False   # 내 파일을 쓰려면 True

if USE_MY_FILE:
    from google.colab import files
    uploaded = files.upload()
    field = load_jsonl(list(uploaded)[0])
else:
    field = load_jsonl(DATA / 'knowledge/sample_field_knowledge.jsonl')
print('워크북 1 지식', len(field), '건')
pd.DataFrame(field)[['id', 'label', 'text', 'stt_raw', 'source']]'''),
    ('code', 'all', '''# 2-2. 새 음성 메모 일괄 전사 → 지식 후보 (아직 검증 전)
new_files = ['voice_red_02.wav', 'voice_blue_02.wav']
candidates = []
for i, name in enumerate(new_files, 1):
    raw = speech_to_text(AUDIO / name)
    text = fix_terms(raw)
    label = '빨강' if '빨강' in text else (
        '파랑' if '파랑' in text else '공통')
    candidates.append({
        'id': f'voice-new-{i:02d}', 'label': label, 'text': text,
        'stt_raw': raw, 'source': name, 'type': 'voice_note',
        'verified': False,
    })
    print(name, '→', text)
    display(Audio(filename=str(AUDIO / name)))'''),
    ('md', 'all', '''### 2-3. 사람 검토 (Human-in-the-loop)
음성을 듣고 바른 문장을 `REVIEW`에 적은 것만 `verified=True`가 된다. **검증되지 않은 지식은 검색에 쓰지 않는다.**'''),
    ('code', 'student', '''# 2-3. 사람 검토: {파일명: 들은 대로 고친 문장}
# ✍️ voice_blue_02.wav를 듣고 바른 문장을 직접 추가해 보자.
REVIEW = {
    'voice_red_02.wav': '빨강 부품에 균열이 보이면 재검사 상자로 옮깁니다.',
    # 'voice_blue_02.wav': '',
}

for c in candidates:
    if REVIEW.get(c['source']):
        c['text'] = REVIEW[c['source']]
        c['verified'] = True
pd.DataFrame(candidates)[['source', 'text', 'verified']]'''),
    ('code', 'teacher', '''# 2-3. 사람 검토: {파일명: 들은 대로 고친 문장}
REVIEW = {
    'voice_red_02.wav': '빨강 부품에 균열이 보이면 재검사 상자로 옮깁니다.',
    'voice_blue_02.wav': '파랑 부품은 한 상자에 스무 개까지만 담습니다.',
}

for c in candidates:
    if REVIEW.get(c['source']):
        c['text'] = REVIEW[c['source']]
        c['verified'] = True
pd.DataFrame(candidates)[['source', 'text', 'verified']]'''),
    T('학생용은 voice_blue_02 검토가 비어 있어 처음엔 검증 지식이 8건, 학생이 문장을 채우면 9건이 된다. “검증되지 않은 자료는 검색 대상에서 제외”가 품질 관리의 핵심.'),
    ('md', 'all', '''## 3. 품질 점검과 병합
- 빈 문장·검증 안 됨 → 제외
- **같은 문장**이 두 번 들어오면(띄어쓰기 무시) → 처음 것 하나만
- 결과를 `rag_knowledge.jsonl`로 저장 = **추가 지식베이스**'''),
    ('code', 'all', '''# 3-1. 점검 · 중복 제거 · 저장
def build_kb(*groups):
    kb, seen = [], set()
    for rows in groups:
        for r in rows:
            if not r.get('verified') or not r.get('text', '').strip():
                print('제외(검증 안 됨/빈 문장):', r.get('source'))
                continue
            key = r['text'].replace(' ', '')
            if key in seen:
                print('제외(중복 문장):', r['source'])
                continue
            seen.add(key)
            kb.append(r)
    return kb


updated = build_kb(base, field, candidates)
save_jsonl(updated, 'rag_knowledge.jsonl')
print('기존', len(base), '건 → 추가 후', len(updated), '건')
pd.DataFrame(updated)[['id', 'label', 'text', 'source']]'''),
    ('md', 'all', '''## 4. 검색(Retrieval) 전/후 비교
**TF-IDF 글자 n-gram**: 문장을 2~3글자 조각으로 나눠 숫자 벡터로 만든다(조사 “은/는/을”이 붙어도 비슷하게 찾음).
**코사인 유사도**: 질문 벡터와 문서 벡터의 방향이 비슷할수록 1에 가깝다. `MIN_SCORE`보다 낮으면 “근거 없음”.'''),
    ('code', 'all', '''# 4-1. 검색기
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MIN_SCORE = 0.25


class Retriever:
    def __init__(self, rows):
        self.rows = rows
        docs = [r['label'] + ' ' + r['text'] for r in rows]
        self.vec = TfidfVectorizer(analyzer='char_wb',
                                   ngram_range=(2, 3))
        self.mat = self.vec.fit_transform(docs)

    def search(self, question, k=2):
        q = self.vec.transform([question])
        scores = cosine_similarity(q, self.mat)[0]
        order = scores.argsort()[::-1][:k]
        return [(float(scores[i]), self.rows[i]) for i in order
                if scores[i] >= MIN_SCORE]


before = Retriever(base)
after = Retriever(updated)
for s, r in after.search('빨강 부품은 어디에 보관해?'):
    print(f'{s:.2f}', r['text'], '|', r['source'])'''),
    ('code', 'all', '''# 4-2. 같은 질문, 전/후 1순위 근거 비교
QUESTIONS = [
    '빨강 부품은 어디에 보관해?',
    '파랑 부품을 보관할 때 주의할 점은?',
    '균열이 보이면 어떻게 해?',
    '작업장 온도는 몇 도로 유지해?',
]


def top1(retriever, q):
    hits = retriever.search(q, k=1)
    if not hits:
        return '근거 없음', 0.0
    return hits[0][1]['text'], round(hits[0][0], 2)


rows = []
for q in QUESTIONS:
    b_text, b_s = top1(before, q)
    a_text, a_s = top1(after, q)
    rows.append([q, b_text, b_s, a_text, a_s])
pd.DataFrame(rows, columns=['질문', '전: 1순위 근거', '전 점수',
                            '후: 1순위 근거', '후 점수'])'''),
    T('예상: 빨강 보관 → 전 “A라인 조립”(관련 단어만 같고 답이 아님) / 후 “왼쪽 상자”. 파랑 주의 → 후 “습기·뚜껑”. 균열 → 후 “재검사 상자” 또는 매뉴얼 “불량 분류”. 온도 → 전·후 모두 근거 없음 = 지식에 없는 것은 답하지 않는다. 모델 재학습 없이 검색 결과가 바뀌었다는 점을 강조.'),
    S('4-2 표를 결과보고 **표 4**에 옮기고, 내가 만든 질문 1개를 `QUESTIONS`에 추가해 다시 실행한 결과도 적는다.'),
    ('md', 'all', '''## 5. 음성 질문 → 검색 → 답변 → 음성(TTS)
마이크(음성 질문) → STT → 교정 → 검색 → 답변 문장 → TTS → 스피커'''),
    ('code', 'all', '''# 5-1. 음성 챗봇 함수
def answer(question):
    hits = after.search(fix_terms(question), k=1)
    if not hits:
        return '관련 지식을 찾지 못했습니다. 현장 기록이 필요합니다.', None
    score, r = hits[0]
    return f"{r['text']} (출처: {r['source']})", r


def voice_chat(wav_path):
    q = speech_to_text(wav_path)
    text, hit = answer(q)
    print('🎙️ 질문(STT):', q)
    print('🔎 교정 질문 :', fix_terms(q))
    print('💬 답변     :', text)
    mp3 = text_to_speech(text.split(' (출처')[0])
    if mp3:
        display(Audio(filename=mp3))
    return text


for name in ['question_01.wav', 'question_02.wav']:
    display(Audio(filename=str(AUDIO / name)))
    voice_chat(AUDIO / name)
    print('-' * 40)'''),
    T('질문 음성도 STT 오류가 섞일 수 있지만 글자 조각 검색이라 핵심 단어(빨강·보관)가 맞으면 근거를 찾는다. 답변은 LLM이 새로 만든 문장이 아니라 검색된 근거를 그대로 읽는 구조(RAG의 R 단계)임을 설명.'),
    ('md', 'all', '''## 6. 핸드폰 음성 챗봇
셀 실행 → QR 스캔 → 🎙️ 질문 녹음(또는 글자로 입력) → `질문하기` → 답변 음성 ▶ 재생.
질문 예: “빨강 부품은 어디에 보관해?”, “파랑 부품 주의할 점은?”, “작업장 온도는?”'''),
    ('code', 'all', QR_UTIL),
    ('code', 'all', '''# 6-1. 핸드폰 음성 챗봇 (Gradio)
import gradio as gr


def ui_chat(audio_path, typed):
    if audio_path:
        wav = to_wav16k(audio_path, 'phone_question.wav')
        q = speech_to_text(wav)
    else:
        q = (typed or '').strip()
    if not q:
        return '', '질문을 녹음하거나 입력하세요.', None, []
    text, hit = answer(q)
    mp3 = text_to_speech(text.split(' (출처')[0])
    hits = [[round(s, 2), r['label'], r['text'], r['source']]
            for s, r in after.search(fix_terms(q), k=3)]
    return q, text, mp3, hits


with gr.Blocks(title='13주 음성 지식 챗봇') as demo:
    gr.Markdown('## 🔊 현장 지식 음성 챗봇')
    mic = gr.Audio(sources=['microphone', 'upload'], type='filepath',
                   label='🎙️ 질문 녹음')
    typed = gr.Textbox(label='또는 글자로 질문')
    ask = gr.Button('질문하기', variant='primary')
    q_out = gr.Textbox(label='인식된 질문(STT)')
    a_out = gr.Textbox(label='답변(근거 + 출처)', lines=2)
    speak = gr.Audio(label='🔊 답변 듣기', type='filepath')
    evid = gr.Dataframe(headers=['점수', '라벨', '근거', '출처'],
                        label='검색된 근거')
    ask.click(ui_chat, [mic, typed], [q_out, a_out, speak, evid])

demo.launch(share=True)
show_qr(demo.share_url)'''),
    S('핸드폰으로 질문 3개(답이 있는 질문 2개, 지식에 없는 질문 1개)를 하고 인식된 질문·답변·출처를 결과보고 **표 5**에 적는다.'),
    ('md', 'all', '''## 7. 결과 저장
`rag_knowledge.jsonl`을 내려받아 결과보고 페이지에 첨부한다.'''),
    ('code', 'all', '''# 7-1. 추가 지식베이스 내려받기
print('최종 지식베이스', len(updated), '건')
try:
    from google.colab import files
    files.download('rag_knowledge.jsonl')
except ImportError:
    print('Colab이 아닌 환경: 파일은 현재 폴더에 있습니다.')'''),
    S('결과보고 **요약**: ① 모델을 다시 학습하지 않고 검색 결과가 바뀐 이유 ② 검증(verified)이 필요한 이유 ③ “근거 없음”이 나온 질문과 그 의미를 각각 1문장으로 적는다.'),
    ('md', 'teacher', '''### 👩‍🏫 정리 질문
1. 지식을 추가하면 Whisper나 색 분류 모델의 가중치가 바뀌나? → 아니오, 검색 대상(지식베이스)만 바뀜
2. STT 원문(stt_raw)을 함께 저장하는 이유? → 추적·재검토
3. “근거 없음”을 답하는 것이 왜 중요한가? → 지어낸 답(환각) 방지'''),
]


def build(cells, who, name):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        'colab': {'provenance': [], 'toc_visible': True},
        'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
        'language_info': {'name': 'python'},
        'accelerator': 'GPU',
    }
    for kind, target, src in cells:
        if target not in ('all', who):
            continue
        if kind == 'md':
            nb.cells.append(nbf.v4.new_markdown_cell(src))
        else:
            nb.cells.append(nbf.v4.new_code_cell(src))
    nbf.write(nb, OUT / name)


OUT.mkdir(parents=True, exist_ok=True)
build(WB1, 'student', 'WB1_student.ipynb')
build(WB1, 'teacher', 'WB1_teacher.ipynb')
build(WB2, 'student', 'WB2_student.ipynb')
build(WB2, 'teacher', 'WB2_teacher.ipynb')
print('built 4 notebooks →', OUT)
