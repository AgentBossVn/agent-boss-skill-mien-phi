# Dán 1 chi tiết THẬT từ ảnh hãng (biển số, ô đèn, nhãn, nút…) vào ảnh AI vẽ, nắn theo phối cảnh, khớp màu, mép mềm.
# Chạy: python dan-chi-tiet-that.py anh-hang.jpg "TL TR BR BL" anh-ai.png "TL TR BR BL" ra.png [khop=0.6] [no=0] [hinh=tu] [mo=0]
#         [--giu "x,y x,y …"]... [--vung "x,y x,y …"] [--co-vao N]      (cờ đặt SAU các tham số vị trí)
#   tứ giác = 4 góc "x,y" theo thứ tự trên-trái, trên-phải, dưới-phải, dưới-trái (đo bằng cat-phong-to.py)
#   khop  0..1: kéo màu/độ sáng chi tiết dán về giống vùng đích (1 = giống hẳn)
#   no    nở mặt nạ thêm bao nhiêu điểm ảnh (che kín mép cũ)
#   hinh  tu = cả tứ giác · vien = hình viên thuốc 2 đầu tròn nằm trong tứ giác (cạnh TL–TR là cạnh ngắn)
#   mo    làm mờ nhẹ ảnh hãng trước khi thu nhỏ (1–1.5 chống răng cưa)
#   --giu   (lặp được) đa giác trên ảnh ĐÍCH mà ảnh AI phải GIỮ NGUYÊN: vật che phía trước chi tiết (tách, ngón tay)
#   --vung  chỉ dán BÊN TRONG đa giác này (ảnh đích) → mép dán chạy theo viền túi/bao, không lộ khung chữ nhật
#   --co-vao N  co tứ giác NGUỒN vào tâm N điểm ảnh trước khi nắn (tránh dính viền nền trắng của ảnh hãng)
#   --khop-vung S  khớp sáng/màu THEO VÙNG thay vì cả mặt: giữ nét chữ của mặt in thật, lấy độ sáng/màu từng vùng của cảnh
#               (S ≈ 40–80 điểm ảnh). Dùng khi mặt in có dải sáng/màu chuyển dần (túi vàng→xanh, nắng rọi 1 bên) → hết lộ khung.
# Mặt nạ cuối = (tứ giác hoặc viên thuốc) ∩ --vung − mọi --giu. Khớp màu chỉ tính trên mặt nạ cuối.
# Dán 1 mặt in lên nhiều cảnh: nắn phẳng 1 lần bằng ep-phang.py rồi dán tấm phẳng vào từng cảnh.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import math, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

def co_goc(q, n):  # mỗi góc nhích vào n điểm ảnh dọc CẢ 2 cạnh kề ⇒ mỗi cạnh lùi vào ~n (đúng cả mặt in dài như biển số)
    q = [np.array(p, float) for p in q]; ra = []
    for i, p in enumerate(q):
        a_, b_ = q[i - 1] - p, q[(i + 1) % 4] - p
        ra.append(tuple(p + n * (a_ / max(np.linalg.norm(a_), 1e-6) + b_ / max(np.linalg.norm(b_), 1e-6))))
    return ra


# tách cờ (--giu lặp được) khỏi tham số vị trí
av, giu, vung, co_vao, khop_vung, i = sys.argv[1:], [], None, 0.0, 0.0, 0
pos = []
while i < len(av):
    if av[i] in ('--giu', '--vung', '--co-vao', '--khop-vung'):
        if i + 1 >= len(av): sys.exit(f'Thiếu giá trị sau {av[i]}')
        if av[i] == '--giu': giu.append(av[i + 1])
        elif av[i] == '--vung': vung = av[i + 1]
        elif av[i] == '--khop-vung': khop_vung = float(av[i + 1])
        else: co_vao = float(av[i + 1])
        i += 2
    else: pos.append(av[i]); i += 1
if len(pos) < 5:
    sys.exit(__doc__ or 'Xem dòng đầu tệp để biết cách chạy')
def tu_giac(s):
    try: return [tuple(map(float, p.split(','))) for p in s.split()]
    except ValueError: sys.exit(f'Toạ độ không đúng dạng "x,y x,y …": {s}')
ref = Image.open(pos[0]).convert('RGB'); src = tu_giac(pos[1])
dst_im = Image.open(pos[2]).convert('RGB'); dst = tu_giac(pos[3])
out = pos[4]
k = float(pos[5]) if len(pos) > 5 else 0.6
no = float(pos[6]) if len(pos) > 6 else 0.0
hinh = pos[7] if len(pos) > 7 else 'tu'
mo = float(pos[8]) if len(pos) > 8 else 0.0
if len(src) != 4 or len(dst) != 4: sys.exit('Mỗi tứ giác phải đủ 4 góc "x,y"')
vung = tu_giac(vung) if vung else None; giu = [tu_giac(g) for g in giu]
if (vung and len(vung) < 3) or any(len(g) < 3 for g in giu): sys.exit('Đa giác --vung/--giu cần ít nhất 3 điểm')
if co_vao > 0: src = co_goc(src, co_vao)
if mo > 0: ref = ref.filter(ImageFilter.GaussianBlur(mo))

A, B = [], []
for (X, Y), (x, y) in zip(dst, src):
    A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
    A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
c = np.linalg.solve(np.array(A), np.array(B))
W, H = dst_im.size
warp = ref.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)

TL, TR, BR, BL = [np.array(p) for p in dst]
def P(u, v): return (1 - v) * ((1 - u) * TL + u * TR) + v * ((1 - u) * BL + u * BR)
if hinh == 'vien':
    rv = 0.5 * np.linalg.norm(TR - TL) / np.linalg.norm(BL - TL); pts = []
    for i in range(0, 181, 6):
        t = math.radians(180 + i); pts.append(P(0.5 + 0.5 * math.cos(t), rv + rv * math.sin(t)))
    for i in range(0, 181, 6):
        t = math.radians(i); pts.append(P(0.5 + 0.5 * math.cos(t), 1 - rv + rv * math.sin(t)))
    poly = [tuple(p) for p in pts]
else:
    poly = [tuple(p) for p in (TL, TR, BR, BL)]
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
if no > 0: m = m.filter(ImageFilter.MaxFilter(int(2 * round(no) + 1)))
if vung:  # chỉ giữ phần nằm trong --vung
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).polygon([tuple(p) for p in vung], fill=255)
    m = ImageChops.multiply(m, v)
for g in giu:  # trừ vùng phải giữ nguyên
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).polygon([tuple(p) for p in g], fill=255)
    m = ImageChops.subtract(m, v)
m = m.filter(ImageFilter.GaussianBlur(0.9))
a = np.asarray(m) / 255.0; sel = a > 0.9
if not sel.any(): sys.exit('Mặt nạ cuối trống (--vung / --giu loại hết vùng dán, hoặc tứ giác đích nằm ngoài ảnh) — kiểm tra lại toạ độ.')
w = np.asarray(warp).astype(float); d = np.asarray(dst_im).astype(float)
if khop_vung > 0:  # tần số thấp (sáng/màu từng vùng) lấy của cảnh, tần số cao (nét chữ) giữ của mặt in thật
    from scipy.ndimage import gaussian_filter
    mk = (a > 0.5).astype(float); mau = gaussian_filter(mk, khop_vung) + 1e-6
    for ch in range(3):
        w[..., ch] += (gaussian_filter(d[..., ch] * mk, khop_vung) - gaussian_filter(w[..., ch] * mk, khop_vung)) / mau
    k = 0.0  # đã khớp theo vùng ⇒ bỏ khớp cả mặt bên dưới
for ch in range(3):
    mw, sw = w[..., ch][sel].mean(), w[..., ch][sel].std() + 1e-6
    md, sd = d[..., ch][sel].mean(), d[..., ch][sel].std()
    w[..., ch] = (w[..., ch] - mw) * (1 + k * (sd / sw - 1)) + (mw + k * (md - mw))
r = d * (1 - a[..., None]) + np.clip(w, 0, 255) * a[..., None]
Image.fromarray(r.astype(np.uint8)).save(out); print('ok', out)
