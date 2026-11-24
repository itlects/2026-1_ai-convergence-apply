"""13주 한국어 음성 샘플 생성(오프라인 TTS) + Whisper-small로 STT 확인."""
import json
import sys
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
M = Path('/tmp/models/vits-mimic3-ko_KO-kss_low')

SENTENCES = {
    # 현장 음성 메모 (WB1/WB2의 추가 지식 원천)
    'voice_red_01.wav': '빨강 부품은 검사 후 왼쪽 상자에 보관합니다.',
    'voice_blue_01.wav': '파랑 부품은 습기에 약하니 뚜껑을 닫아 보관합니다.',
    'voice_red_02.wav': '빨강 부품에 균열이 보이면 재검사 상자로 옮깁니다.',
    'voice_blue_02.wav': '파랑 부품은 한 상자에 스무 개까지만 담습니다.',
    # 음성 질문 (WB2 챗봇)
    'question_01.wav': '빨강 부품은 어디에 보관해?',
    'question_02.wav': '파랑 부품을 보관할 때 주의할 점은?',
}

cfg = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=str(M / 'ko_KO-kss_low.onnx'),
            tokens=str(M / 'tokens.txt'),
            data_dir=str(M / 'espeak-ng-data'),
        ),
        num_threads=2,
    ),
)
tts = sherpa_onnx.OfflineTts(cfg)


def save_wav16k(path, samples, sr):
    x = np.asarray(samples, dtype=np.float32)
    if sr != 16000:
        t_old = np.arange(len(x)) / sr
        t_new = np.arange(int(len(x) * 16000 / sr)) / 16000
        x = np.interp(t_new, t_old, x)
    pad = np.zeros(int(0.3 * 16000), dtype=np.float32)
    x = np.concatenate([pad, x, pad])
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    pcm = (x * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(pcm.tobytes())


for name, text in SENTENCES.items():
    audio = tts.generate(text, sid=0, speed=0.9)
    save_wav16k(OUT / name, audio.samples, audio.sample_rate)

(OUT / 'voice_reference.json').write_text(
    json.dumps(SENTENCES, ensure_ascii=False, indent=1), encoding='utf-8')
print('saved', len(SENTENCES))
