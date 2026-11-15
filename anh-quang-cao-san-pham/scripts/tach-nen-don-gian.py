# Tách nền KHÔNG cần Mac, cho ảnh hãng nền trắng/trơn: ra PNG trong suốt, cắt sát sản phẩm. Thay tach-nen-san-pham.swift khi không có Mac.
# Màu nền = trung vị viền ngoài 2% ảnh; điểm lệch màu nền ≤ ngưỡng VÀ nối với viền ngoài → nền. Vùng "trắng" nằm kín trong sản phẩm được giữ.
# Còn lại: giữ thành phần liên thông lớn nhất, lấp lỗ, làm mềm mép 1px, cắt sát hộp bao. Nền có bóng/gradient/nền đậm không hợp → dùng đường khác.
# Giới hạn: lỗ XUYÊN qua sản phẩm (quai cốc, quai túi) bị giữ thành mảng màu nền → sản phẩm có lỗ xuyên thì dùng đường khác.
# Chạy: python tach-nen-don-gian.py vao.jpg ra.png [--nguong 18]   (nền còn sót → tăng ngưỡng; ăn vào sản phẩm → giảm)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument('vao'); ap.add_argument('ra')
ap.add_argument('--nguong', type=float, default=18, help='khoảng cách màu RGB tối đa so với nền')
a = ap.parse_args()

im = ImageOps.exif_transpose(Image.open(a.vao)).convert('RGBA')  # ảnh chụp điện thoại: xoay đúng chiều
rgb = np.asarray(im.convert('RGB')).astype(np.float32); H, W = rgb.shape[:2]
b = max(2, round(min(H, W) * 0.02))
vien = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3), rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
nen_mau = np.median(vien, axis=0)
gan_nen = np.linalg.norm(rgb - nen_mau, axis=2) <= a.nguong
lab, n = ndimage.label(gan_nen)
cham_vien = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); cham_vien = cham_vien[cham_vien > 0]
nen = np.isin(lab, cham_vien)  # chỉ vùng gần màu nền mà NỐI viền ngoài mới là nền
vat = ~nen
lab2, n2 = ndimage.label(vat)
if n2 == 0: raise SystemExit('LỖI không còn gì sau khi bỏ nền — giảm --nguong.')
lon = np.argmax(ndimage.sum(vat, lab2, range(1, n2 + 1))) + 1
vat = ndimage.binary_fill_holes(lab2 == lon)
alpha = Image.fromarray((vat * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))  # mép mềm ~1px
im.putalpha(alpha)
im = im.crop(alpha.point(lambda v: 255 if v > 8 else 0).getbbox())
im.save(a.ra)
print(f'OK {a.ra} · {im.width}x{im.height} · nền ≈ RGB{tuple(int(x) for x in nen_mau)} · giữ {vat.mean() * 100:.0f}% diện tích ảnh')
