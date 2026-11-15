# Ép phẳng 1 mặt in (mặt trước hộp, bìa sách, mặt túi) trong ảnh hãng thành tấm chữ nhật thẳng rong×cao.
# Chạy: python ep-phang.py anh-hang.jpg "TL TR BR BL" rong cao ra.png [--mo 0] [--co-vao 0]
#   tứ giác = 4 góc "x,y" của mặt in trên ảnh hãng: trên-trái, trên-phải, dưới-phải, dưới-trái (đo bằng cat-phong-to.py)
#   --mo N      làm mờ nhẹ ảnh hãng trước khi nắn (1–1.5 chống răng cưa khi thu nhỏ)
#   --co-vao N  co tứ giác vào tâm N điểm ảnh (tránh dính viền nền trắng của ảnh hãng)
# Dùng 2 bước: (1) ép phẳng 1 lần → ra.png (rong×cao)
#   (2) dán tấm phẳng vào MỌI cảnh, 4 góc đích đo trên từng ảnh AI:
#   python dan-chi-tiet-that.py ra.png "0,0 W,0 W,H 0,H" anh-ai.png "<4 góc đích>" canh-1.png   (W,H = rong,cao đã ép)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import math, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

def co_goc(q, n):  # mỗi góc nhích vào n điểm ảnh dọc CẢ 2 cạnh kề ⇒ mỗi cạnh lùi vào ~n (đúng cả mặt in dài như biển số)
    q = [np.array(p, float) for p in q]; ra = []
    for i, p in enumerate(q):
        a_, b_ = q[i - 1] - p, q[(i + 1) % 4] - p
        ra.append(tuple(p + n * (a_ / max(np.linalg.norm(a_), 1e-6) + b_ / max(np.linalg.norm(b_), 1e-6))))
    return ra


av, mo, co_vao, pos, i = sys.argv[1:], 0.0, 0.0, [], 0
while i < len(av):
    if av[i] in ('--mo', '--co-vao'):
        if i + 1 >= len(av): sys.exit(f'Thiếu giá trị sau {av[i]}')
        if av[i] == '--mo': mo = float(av[i + 1])
        else: co_vao = float(av[i + 1])
        i += 2
    else: pos.append(av[i]); i += 1
if len(pos) < 5: sys.exit('Cách chạy: python ep-phang.py anh-hang.jpg "TL TR BR BL" rong cao ra.png [--mo 0] [--co-vao 0]')
try: q = [tuple(map(float, p.split(','))) for p in pos[1].split()]
except ValueError: sys.exit('Toạ độ không đúng dạng "x,y x,y x,y x,y"')
if len(q) != 4: sys.exit('Tứ giác phải đủ 4 góc "x,y"')
rong, cao = int(pos[2]), int(pos[3])
if rong < 1 or cao < 1: sys.exit('rong, cao phải > 0')
ref = ImageOps.exif_transpose(Image.open(pos[0])).convert('RGB')
if mo > 0: ref = ref.filter(ImageFilter.GaussianBlur(mo))
if co_vao > 0: q = co_goc(q, co_vao)
dst = [(0, 0), (rong, 0), (rong, cao), (0, cao)]
A, B = [], []
for (X, Y), (x, y) in zip(dst, q):
    A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
    A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
c = np.linalg.solve(np.array(A), np.array(B))
ref.transform((rong, cao), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).save(pos[4]); print('ok', pos[4])
