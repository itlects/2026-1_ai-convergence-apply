"""핸드폰으로 책상 위 색종이/부품을 찍은 듯한 합성 사진 생성 (640x480 JPG)."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(sys.argv[1])
rng = np.random.default_rng(13)

COLORS = {
    'red': [(205, 40, 45), (185, 30, 50), (225, 65, 55), (170, 35, 35), (215, 50, 70)],
    'blue': [(35, 60, 200), (30, 80, 180), (55, 70, 225), (25, 50, 160), (60, 95, 205)],
}
TEST = {
    'test_red_01': (195, 45, 50),
    'test_red_shadow': (120, 28, 32),
    'test_blue_01': (40, 75, 195),
    'test_green_01': (40, 160, 70),
    'test_white_01': (225, 225, 220),
}


def photo(color, seed):
    r = np.random.default_rng(seed)
    w, h = 640, 480
    base = np.array([150, 120, 90]) + r.integers(-20, 20, 3)  # 나무 책상
    yy, xx = np.mgrid[0:h, 0:w]
    grain = (np.sin(yy / 7 + r.random() * 6) * 8)[..., None]
    img = np.clip(base + grain, 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    paper = Image.new('RGB', (300, 230), color)
    ang = float(r.uniform(-15, 15))
    mask = Image.new('L', paper.size, 255).rotate(ang, expand=True)
    paper = paper.rotate(ang, expand=True)
    cx = w // 2 + int(r.integers(-30, 30))
    cy = h // 2 + int(r.integers(-25, 25))
    im.paste(paper, (cx - paper.width // 2, cy - paper.height // 2), mask)
    a = np.asarray(im).astype(float)
    light = 0.85 + 0.3 * (xx / w) * r.uniform(0.5, 1.0)  # 조명 기울기
    a = a * light[..., None] + r.normal(0, 6, a.shape)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return out.filter(ImageFilter.GaussianBlur(0.8))


for label, cols in COLORS.items():
    d = OUT / 'train' / label
    d.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(cols, 1):
        photo(c, i + (0 if label == 'red' else 100)).save(d / f'{label}_{i:02d}.jpg', quality=88)

(OUT / 'test').mkdir(parents=True, exist_ok=True)
for i, (name, c) in enumerate(TEST.items()):
    photo(c, 500 + i).save(OUT / 'test' / f'{name}.jpg', quality=88)
print('ok')
