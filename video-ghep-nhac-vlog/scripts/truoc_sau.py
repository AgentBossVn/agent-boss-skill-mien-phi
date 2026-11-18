# Bản "trước – sau" để khoe: video gốc (bên trái) và thành phẩm (bên phải) chạy song song ~10 giây, khung dọc 9:16 đăng được ngay.
# Chạy sau dung.py: python3 scripts/truoc_sau.py <thư-mục-làm-việc>/ke-hoach.json [--giay 10]
# Ra: thanh-pham/video-truoc-sau.mp4 (cạnh video thành phẩm)
import argparse, os
from chung import W, H, FPS, ENC, AENC, run, doc_json, thuong_hieu, mau, tim_font, thong_tin, log  # nạp trước: tự đổi sang Python riêng
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('ke_hoach')
ap.add_argument('--giay', type=float, default=10)
a = ap.parse_args()
KH = doc_json(a.ke_hoach)
GOC = os.path.dirname(os.path.abspath(a.ke_hoach))
TH = thuong_hieu(KH.get('thuong_hieu') and os.path.join(GOC, KH['thuong_hieu']))
OUT = os.path.join(GOC, KH.get('dau_ra', 'thanh-pham/video.mp4'))
if not os.path.exists(OUT):
    raise SystemExit(f'Chưa có thành phẩm {OUT}: chạy dung.py trước')
d0 = KH['doan'][0]
NGUON = os.path.join(GOC, d0['file'])
giay = min(a.giay, thong_tin(OUT)['dai'])

# 2 ô 9:16 cạnh nhau, chữ TRƯỚC / SAU phía trên, tên kênh phía dưới
ow, oh = 504, 896
x1, x2, y = (W - 2 * ow) // 3, (W - 2 * ow) // 3 * 2 + ow, (H - oh) // 2 + 30
nen = Image.new('RGBA', (W, H), mau(TH['mau_chinh']))
v = ImageDraw.Draw(nen)
f_nhan = ImageFont.truetype(tim_font(TH.get('font')), 84)
f_ten = ImageFont.truetype(tim_font(TH.get('font')), 46)
for x, chu, m in ((x1, 'TRƯỚC', mau(TH['mau_chu'])), (x2, 'SAU', mau(TH['mau_nhan']))):
    v.text((x + ow / 2, y - 40), chu, font=f_nhan, fill=m, anchor='md', stroke_width=4, stroke_fill=(0, 0, 0))
    v.rounded_rectangle((x - 6, y - 6, x + ow + 6, y + oh + 6), 18, outline=m, width=6)
if TH.get('ten'):
    v.text((W / 2, y + oh + 90), TH['ten'], font=f_ten, fill=mau(TH['mau_chu']), anchor='mm')
tam = os.path.join(os.path.dirname(OUT), '.nen-truoc-sau.png')
nen.save(tam)

o = f'scale={ow}:{oh}:force_original_aspect_ratio=decrease,pad={ow}:{oh}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS}'
ra = os.path.join(os.path.dirname(OUT), 'video-truoc-sau.mp4')
run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', tam,
     '-t', f'{giay:.2f}', '-i', NGUON,   # gốc chạy từ đầu, nguyên chỗ lặng, ấp úng: thấy rõ khác biệt
     '-t', f'{giay:.2f}', '-i', OUT,
     '-filter_complex', f'[1:v]{o}[a];[2:v]{o}[b];[0:v][a]overlay={x1}:{y}[t];[t][b]overlay={x2}:{y},'
                        f'fade=t=out:st={giay - 0.4:.2f}:d=0.4[v];[2:a]afade=t=out:st={giay - 0.6:.2f}:d=0.6[am]',
     '-map', '[v]', '-map', '[am]', '-t', f'{giay:.2f}', *ENC, *AENC, '-movflags', '+faststart', ra])
os.remove(tam)
log(f'Bản trước – sau: {ra}')
print(ra)
