# Thay logo AI vẽ méo bằng logo THẬT: (1) xoá logo cũ trong hộp bằng cách loang màu nền xung quanh,
# (2) in logo lấy từ ảnh hãng (tứ giác nguồn) vào tứ giác đích, màu theo màu logo cũ.
# Hợp với logo 1 màu sáng trên nền tối (logo tối trên nền sáng: thêm --toi-tren-sang). Logo nhiều màu → dan-chi-tiet-that.py.
# Chạy: python thay-logo.py anh-hang.jpg "TL TR BR BL" anh-ai.png "TL TR BR BL" "x0,y0,x1,y1" ra.png [mo=1.0] [--toi-tren-sang]
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

args = [x for x in sys.argv[1:] if not x.startswith('--')]; toi = '--toi-tren-sang' in sys.argv
if len(args) < 6:
    sys.exit('Cách chạy: python thay-logo.py anh-hang.jpg "TL TR BR BL" anh-ai.png "TL TR BR BL" "x0,y0,x1,y1" ra.png [mo]')
def tu_giac(s): return [tuple(map(float, p.split(','))) for p in s.split()]
ref = Image.open(args[0]).convert('L'); src = tu_giac(args[1])
dimg = Image.open(args[2]).convert('RGB'); dst = tu_giac(args[3])
x0, y0, x1, y1 = map(int, args[4].split(',')); out = args[5]; mo = float(args[6]) if len(args) > 6 else 1.0
d = np.asarray(dimg).astype(float); W, H = dimg.size
# 1. xoá logo cũ: điểm ảnh khác hẳn nền trong hộp → loang màu nền vào
box = d[y0:y1, x0:x1]; L = box.mean(2)
if toi: L = 255 - L
p50, p95 = np.percentile(L, 50), np.percentile(L, 95)
cu = ndimage.binary_dilation(L > p50 + 0.45 * (p95 - p50), iterations=2)
mau_logo = np.percentile(box[cu].reshape(-1, 3), 15 if toi else 85, axis=0) if cu.any() else np.array([220., 220., 220.])
pad = 12; X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
reg = d[Y0:Y1, X0:X1].copy(); hong = np.zeros(reg.shape[:2], bool); hong[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = cu
ok = (~hong).astype(float); fill = reg.copy()
for _ in range(6):
    for ch in range(3):
        num = ndimage.gaussian_filter(fill[..., ch] * ok, 3); den = ndimage.gaussian_filter(ok, 3) + 1e-6
        fill[..., ch] = np.where(hong, num / den, reg[..., ch])
    ok = np.maximum(ok, (ndimage.gaussian_filter(ok, 3) > 0.3).astype(float))
d[Y0:Y1, X0:X1] = fill
# 2. in logo thật: nắn phối cảnh, độ sáng logo hãng làm độ phủ, tô bằng màu logo cũ
A, B = [], []
for (X, Y), (x, y) in zip(dst, src):
    A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
    A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
c = np.linalg.solve(np.array(A), np.array(B))
if mo > 0: ref = ref.filter(ImageFilter.GaussianBlur(mo))
wl = np.asarray(ref.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)).astype(float)
if toi: wl = 255 - wl
q = Image.new('L', (W, H), 0); ImageDraw.Draw(q).polygon(dst, fill=255); q = np.asarray(q) / 255.0
nen, sang = np.percentile(wl[q > 0.5], 30), np.percentile(wl[q > 0.5], 99)
a = np.clip((wl - nen) / max(1, sang - nen), 0, 1) ** 1.2 * q
r = d * (1 - a[..., None]) + mau_logo * a[..., None]
Image.fromarray(np.clip(r, 0, 255).astype(np.uint8)).save(out); print('ok', out, 'màu logo', mau_logo.round())
