"""Whisper-small(오픈AI 가중치, ONNX 변환본)으로 WAV 전사 확인."""
import sys
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

W = Path('/tmp/models/sherpa-onnx-whisper-small')
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=str(W / 'small-encoder.int8.onnx'),
    decoder=str(W / 'small-decoder.int8.onnx'),
    tokens=str(W / 'small-tokens.txt'),
    language='ko',
    task='transcribe',
    num_threads=2,
)


def transcribe(path):
    with wave.open(str(path), 'rb') as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), '<i2')
    s = rec.create_stream()
    s.accept_waveform(sr, x.astype(np.float32) / 32768)
    rec.decode_stream(s)
    return s.result.text.strip()


if __name__ == '__main__':
    for p in sorted(Path(sys.argv[1]).glob('*.wav')):
        print(p.name, '→', transcribe(p))
