# Ghép nhiều ảnh (hoặc 1 vùng cắt của ảnh) thành 1 ảnh ngang có nhãn — để soát và để cho người duyệt xem trước/sau.
# Chạy: python so-sanh-truoc-sau.py ra.jpg "Trước khi soát=ve/a.png@1600,630,1720,830" "Sau khi sửa=sua/a.png@1600,630,1720,830" "Ảnh hãng=hang/mat-truoc.jpg"
#   @x0,y0,x1,y1 (không bắt buộc) = chỉ lấy vùng đó. Mọi ảnh đưa về cùng chiều cao (biến CAO, mặc định 760);
#   tổng bề rộng tự giới hạn ở RONG_TOI_DA (mặc định 3000) để ảnh ghép còn đọc được.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import os, sys
from PIL import Image, ImageDraw, ImageFont

PHONG = [os.path.expanduser('~/Library/Fonts/BeVietnamPro-Bold.ttf'), '/Library/Fonts/Arial Unicode.ttf',
         '/System/Library/Fonts/Supplemental/Arial Bold.ttf', r'C:\Windows\Fonts\arialbd.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
def phong(n):
    for p in PHONG:
        if os.path.exists(p): return ImageFont.truetype(p, n)
    return ImageFont.load_default(size=n)

if len(sys.argv) < 3: sys.exit('Cách chạy: python so-sanh-truoc-sau.py ra.jpg "Nhãn=anh.png[@x0,y0,x1,y1]" ...')
H = int(os.environ.get('CAO', 760)); co = 34; pad, top = 24, co + 36
ds = []
for arg in sys.argv[2:]:
    nhan, duong = arg.split('=', 1)
    duong, _, vung = duong.partition('@')
    im = Image.open(duong).convert('RGB')
    if vung: im = im.crop(tuple(map(int, vung.split(','))))
    ds.append((nhan, im))
# vùng cắt ngang dài → ảnh ghép quá rộng không đọc được: hạ chiều cao cho tổng bề rộng ≤ RONG_TOI_DA
rong_toi_da, le = int(os.environ.get('RONG_TOI_DA', 3000)), pad * (len(ds) + 1)
tong = sum(im.width * H / im.height for _, im in ds)
if tong + le > rong_toi_da: H = max(200, int(H * (rong_toi_da - le) / tong))
tam = [(nhan, im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS)) for nhan, im in ds]
W = sum(im.width for _, im in tam) + pad * (len(tam) + 1)
out = Image.new('RGB', (W, H + top + pad), (247, 245, 242)); d = ImageDraw.Draw(out); x = pad
for nhan, im in tam:
    d.text((x, 18), nhan, font=phong(co), fill=(30, 30, 30)); out.paste(im, (x, top)); x += im.width + pad
out.save(sys.argv[1], quality=90); print('ok', sys.argv[1], out.size)
