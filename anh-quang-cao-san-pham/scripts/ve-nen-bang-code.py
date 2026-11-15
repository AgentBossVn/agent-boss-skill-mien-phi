# Vẽ nền studio bằng CODE (đường "Agent tự dựng": không AI, 0đ, không Chrome) rồi ghép sản phẩm thật bằng ghep-san-pham-that.py + dat-chu.py.
# kieu toi : radial từ màu chính sáng ở tâm (50% ngang, 58% cao) ra màu phụ/tối ở góc; --vong thêm 2 vòng tròn mảnh vàng nhạt.
# kieu sang: nền kem pha nhẹ màu chính, mặt sàn sáng hơn ở 30% dưới, chuyển mềm. Cả hai thêm hạt ±2 chống sọc màu.
# Chạy: python ve-nen-bang-code.py --mau-chinh "#d4202a" [--mau-phu "#3a0508"] [--kieu toi|sang] [--vong] --co 1080x1350 1920x1080 --ra thu-muc
#       → thu-muc/nen-<rộng>x<cao>.png (mỗi cỡ 1 tệp)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, os
import numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('--mau-chinh', required=True); ap.add_argument('--mau-phu', default='')
ap.add_argument('--kieu', default='toi', choices=['toi', 'sang']); ap.add_argument('--vong', action='store_true')
ap.add_argument('--co', nargs='+', required=True, help='vd 1080x1350'); ap.add_argument('--ra', required=True)
a = ap.parse_args()


def mau(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

def tron(c1, c2, t): return c1 + (c2 - c1) * t[..., None]  # t 0→1: c1→c2

chinh = mau(a.mau_chinh)
phu = mau(a.mau_phu) if a.mau_phu else chinh * 0.18  # mặc định: tối từ chính nó
os.makedirs(a.ra, exist_ok=True)
rng = np.random.default_rng(7)
for co in a.co:
    W, H = (int(x) for x in co.lower().split('x'))
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if a.kieu == 'toi':
        # tâm 50%/58%; t=0 ở tâm, 1 ở góc xa nhất (thang dừng 0 / .38 / .75 / 1 như bản HTML)
        t = np.hypot(x - W * .5, y - H * .58) / np.hypot(W * .5, H * .58)
        giua = chinh * 0.74 + phu * 0.26; goc = phu * 0.45
        d = np.where(t[..., None] < .38, tron(chinh, giua, np.clip(t / .38, 0, 1)),
            np.where(t[..., None] < .75, tron(giua, phu, np.clip((t - .38) / .37, 0, 1)), tron(phu, goc, np.clip((t - .75) / .25, 0, 1))))
    else:
        kem = np.array([246, 239, 226], np.float32); kem2 = np.array([226, 210, 180], np.float32)
        nen = tron(kem, kem2, np.clip(x / W * .35 + y / H * .65, 0, 1))  # chéo nhẹ kem sáng → kem sẫm
        nen = nen * 0.9 + (chinh * 0.35 + 255 * 0.65) * 0.1  # pha nhẹ màu chính
        san = np.clip((y / H - .70) / .30, 0, 1)  # mặt sàn từ 70% xuống: sáng hơn, mượt
        san = (san * san * (3 - 2 * san))[..., None]
        d = nen * (1 - san * 0.6) + np.array([255, 250, 240], np.float32) * san * 0.6
    d = np.clip(d + rng.integers(-2, 3, (H, W, 1)), 0, 255).astype(np.uint8)
    im = Image.fromarray(d)
    if a.vong and a.kieu == 'toi':
        lop = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dv = ImageDraw.Draw(lop); cx, cy, m = W * .5, H * .58, min(W, H)
        for k, al in ((.83, 64), (1.09, 30)):  # 2 vòng, vòng ngoài nhạt hơn (alpha .25 / .12)
            r = m * k / 2; dv.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 214, 90, al), width=max(2, round(m / 540)))
        im = Image.alpha_composite(im.convert('RGBA'), lop).convert('RGB')
    p = os.path.join(a.ra, f'nen-{W}x{H}.png'); im.save(p); print('ra', p)
