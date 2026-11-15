# Cắt 1 vùng ảnh, phóng to, kẻ lưới có số toạ độ điểm ảnh — để soát chi tiết và đo chỗ dán.
# Chạy: python cat-phong-to.py ra.jpg anh.png x0 y0 x1 y1 [phong=4] [buoc=10]
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import sys
from PIL import Image, ImageDraw

if len(sys.argv) < 7:
    sys.exit('Cách chạy: python cat-phong-to.py ra.jpg anh.png x0 y0 x1 y1 [phong=4] [buoc=10]')
ra, vao = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
s = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
st = int(sys.argv[8]) if len(sys.argv) > 8 else 10
im = Image.open(vao).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
d = ImageDraw.Draw(im)
for x in range((x0 // st + 1) * st, x1, st):
    X = (x - x0) * s; dam = x % (st * 5) == 0
    d.line([(X, 0), (X, im.height)], fill=(0, 255, 255) if dam else (0, 140, 140), width=1)
    if dam: d.text((X + 2, 2), str(x), fill=(255, 255, 0))
for y in range((y0 // st + 1) * st, y1, st):
    Y = (y - y0) * s; dam = y % (st * 5) == 0
    d.line([(0, Y), (im.width, Y)], fill=(0, 255, 255) if dam else (0, 140, 140), width=1)
    if dam: d.text((2, Y + 2), str(y), fill=(255, 255, 0))
im.save(ra, quality=90); print(ra, im.size)
