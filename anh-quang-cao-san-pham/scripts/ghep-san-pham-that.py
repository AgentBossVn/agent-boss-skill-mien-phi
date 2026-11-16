# Ghép ẢNH THẬT của sản phẩm (đã tách nền, PNG trong suốt) lên 1 ảnh cảnh trống, thêm bóng đổ cho thật.
# Dùng cho đường "ghép": AI chỉ vẽ cảnh KHÔNG có sản phẩm, sản phẩm giữ đúng 100% như ảnh hãng.
# Chạy: python ghep-san-pham-that.py nen.png vat.png ra.png --cao 0.55 --tam-x 0.5 --day-y 0.72 [--bong phai|trai|khong]
#   --cao   : chiều cao sản phẩm / chiều cao ảnh (máy cảnh báo khi sản phẩm phải phóng gần bằng / quá ảnh gốc → mờ)
#   --tam-x : giữa sản phẩm nằm ở đâu theo chiều ngang (0 = mép trái, 1 = mép phải)
#   --day-y : đáy sản phẩm chạm mặt bàn ở đâu theo chiều dọc (0 = trên cùng, 1 = dưới cùng)
#   --bong  : bóng đổ về phía nào (ngược phía nguồn sáng của cảnh). Mặc định phải (đèn bên trái).
#   --hoa-mau: kéo màu/độ sáng sản phẩm về tông cảnh quanh chỗ đặt (0 = giữ nguyên ảnh hãng, mặc định 0.3).
#              Không có bước này sản phẩm sáng/lạnh hơn cảnh, nhìn như dán (sách ghép cảnh tối ấm 16/11/2026).
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse
from PIL import Image, ImageFilter, ImageDraw, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('nen'); ap.add_argument('vat'); ap.add_argument('ra')
ap.add_argument('--cao', type=float, default=0.55)
ap.add_argument('--tam-x', type=float, default=0.5)
ap.add_argument('--day-y', type=float, default=0.75)
ap.add_argument('--bong', default='phai', choices=['phai', 'trai', 'khong'])
ap.add_argument('--dam', type=float, default=1.0, help='độ đậm bóng (0.5 nhạt … 1.5 đậm)')
ap.add_argument('--hoa-mau', type=float, default=0.3, help='0..1: kéo tông sản phẩm về tông cảnh quanh chỗ đặt')
a = ap.parse_args()

nen = Image.open(a.nen).convert('RGB'); W, H = nen.size
vat = Image.open(a.vat).convert('RGBA')
bb = vat.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()  # cắt sát phần có sản phẩm
vat = vat.crop(bb)
h = round(H * a.cao); w = round(vat.width * h / vat.height)
ti = h / vat.height  # >0,8 = hiện gần bằng / to hơn ảnh gốc → mờ (đo 16/11: hộp cà phê ảnh gốc cao 481px bị hiện 567px (×1,18) nhìn nhoè)
if ti > 0.8:
    print(f'CẢNH BÁO sản phẩm hiện bằng {ti:.0%} cỡ ảnh gốc ({vat.width}x{vat.height}) → sẽ MỜ. '
          f'Hạ --cao xuống ≤ {0.8 * vat.height / H:.2f}, hoặc xin ảnh hãng to + nét hơn (chụp sản phẩm thật, file thiết kế bao bì).')
toi_thieu = 0.5 if W > H * 1.2 else 0.36 if H > W * 1.5 else 0.42  # ảnh học viên 16/11: sách cao 33–40% khung trên bàn trống → "xấu", khách không thấy sản phẩm
if a.cao < toi_thieu:
    print(f'CẢNH BÁO sản phẩm NHỎ: cao {a.cao:.0%} khung (ảnh {W}x{H} nên ≥ {toi_thieu:.0%}). Lướt điện thoại sẽ không thấy sản phẩm. '
          'Tăng --cao; cảnh không cho phép (sản phẩm to quá so với đồ vật quanh) → vẽ lại cảnh CẬN hơn (máy đặt thấp, sát mặt bàn), KHÔNG giao ảnh có cảnh báo này.')
vat = vat.resize((w, h), Image.LANCZOS)
x = round(W * a.tam_x - w / 2); y = round(H * a.day_y - h)
if a.hoa_mau > 0:  # khớp tông: nhân từng kênh màu theo tỉ lệ (màu trung bình cảnh quanh chỗ đặt / màu trung bình sản phẩm)
    from PIL import ImageStat
    quanh = nen.crop((max(0, x - w // 2), max(0, y), min(W, x + w + w // 2), min(H, y + h)))
    mc = ImageStat.Stat(quanh).mean; mv = ImageStat.Stat(vat.convert('RGB'), vat.getchannel('A')).mean
    sang_c, sang_v = max(sum(mc) / 3, 1), max(sum(mv) / 3, 1)
    he = [1 + a.hoa_mau * ((c / sang_c) / max(v / sang_v, 1e-3) - 1) for c, v in zip(mc, mv)]  # sắc (ấm/lạnh)
    he = [k * (1 + a.hoa_mau * 0.5 * (min(sang_c / sang_v, 1.15) - 1)) for k in he]  # độ sáng, kéo nhẹ hơn sắc
    r, g, b, al = vat.split()
    vat = Image.merge('RGBA', [ch.point(lambda v, k=k: min(255, round(v * k))) for ch, k in zip((r, g, b), he)] + [al])
alpha = vat.getchannel('A')
lop = Image.new('RGBA', (W, H), (0, 0, 0, 0))

# 1) Bóng đổ dài: bóng sản phẩm ép dẹt, nghiêng theo hướng sáng, làm mờ.
if a.bong != 'khong':
    cao_b = max(4, round(h * 0.22)); ngang = round(h * 0.55)
    s = alpha.resize((w, cao_b))
    rong = w + ngang
    bong = Image.new('L', (rong, cao_b), 0)
    for r in range(cao_b):  # dòng trên cùng của bóng (ngọn sản phẩm) dịch xa nhất
        dich = round(ngang * (1 - r / cao_b))
        bong.paste(s.crop((0, r, w, r + 1)), (dich if a.bong == 'phai' else ngang - dich, r))
    bong = bong.point(lambda v: int(v * 0.30 * a.dam)).filter(ImageFilter.GaussianBlur(max(3, h * 0.02)))
    toan = Image.new('L', (W, H), 0)  # dán lên khung đủ cỡ: paste chịu được toạ độ âm / tràn mép
    toan.paste(bong, (x if a.bong == 'phai' else x - ngang, y + h - cao_b))
    den = Image.new('RGBA', (W, H), (25, 20, 15, 0)); den.putalpha(toan)
    lop.alpha_composite(den)

# 2) Bóng chạm: chính hình sản phẩm dịch xuống ~1% và làm mờ ⇒ bóng bám ĐÚNG mép đáy (đáy nghiêng 3/4 cũng chạm bàn).
#    Elip nằm ngang cũ để hở phần đáy cao hơn ⇒ sản phẩm trông lơ lửng (sách ghép 16/11/2026).
cham = Image.new('L', (W, H), 0); cham.paste(alpha.point(lambda v: int(v * 0.75 * min(a.dam, 1.3))), (x, y + max(2, round(h * 0.012))))
cham = cham.filter(ImageFilter.GaussianBlur(max(2, h * 0.008)))
den = Image.new('RGBA', (W, H), (20, 15, 10, 0)); den.putalpha(cham)
lop.alpha_composite(den)

lop.alpha_composite(vat, (x, y))
out = nen.convert('RGBA'); out.alpha_composite(lop)
out.convert('RGB').save(a.ra)
print(f'OK {a.ra} · sản phẩm {w}x{h} tại ({x},{y})')
