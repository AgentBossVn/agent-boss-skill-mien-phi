# Vẽ 1 ảnh MIỄN PHÍ bằng FLUX.2 [klein] trên Cloudflare Workers AI, kèm tối đa 4 ảnh mẫu chính hãng.
# Miễn phí = nằm trong 10.000 "neuron"/ngày Cloudflare cho mọi tài khoản (kể cả gói Free). Máy tự đếm neuron
# theo bảng giá Cloudflare, ghi sổ, và TỪ CHỐI vẽ khi lượt này làm vượt mức miễn phí trong ngày (giờ UTC).
# Cần: tài khoản Cloudflare (miễn phí) + 1 trong 2 cách:
#   (a) biến môi trường CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN (token tạo ở dash.cloudflare.com, mẫu "Workers AI")
#   (b) --cong http://127.0.0.1:8841  — cổng chạy bằng `wrangler dev` dùng đăng nhập wrangler sẵn có (xem SKILL.md)
# Máy KHÔNG in token ra.
# Chạy: python ve-anh-mien-phi.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.jpg anh-hang/b.jpg --ti-le 4:5 --ra ve/canh-1-a.png
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, base64, datetime, io, json, os, re, sys, time, urllib.error, urllib.request, uuid
from PIL import Image, ImageOps

# Chỉ dùng klein-4b: ~200–250 neuron/ảnh ⇒ ~40 ảnh/ngày miễn phí. (klein-9b ~2.000 neuron/ảnh và báo lỗi 3043 khi thử 14/11/2026.)
MODEL = {'klein-4b': '@cf/black-forest-labs/flux-2-klein-4b'}
KHUNG = {'1:1': (1024, 1024), '4:5': (1024, 1280), '9:16': (1024, 1824), '16:9': (1824, 1024),
         '3:4': (1024, 1360), '4:3': (1360, 1024)}  # bội số 16, cạnh dài ≤ 1920 (giới hạn model)
MIEN_PHI_NGAY = 10_000  # neuron/ngày, developers.cloudflare.com/workers-ai/platform/pricing (đọc 14/11/2026)


def o_512(w, h): return -(-w // 512) * -(-h // 512)


def uoc_neuron(w, h, mau):  # bảng giá Cloudflare flux-2-klein-4b 11/2026: 26,05/ô 512 ảnh ra + 5,37/ô 512 ảnh vào
    return 26.05 * o_512(w, h) + sum(5.37 * o_512(*s) for s in mau)


ap = argparse.ArgumentParser(description='Vẽ ảnh miễn phí (Cloudflare Workers AI, FLUX.2 klein), kèm ảnh mẫu hãng')
ap.add_argument('--loi-nho', required=True)
ap.add_argument('--mau', nargs='*', default=[], help='tối đa 4 ảnh mẫu chính hãng')
ap.add_argument('--ti-le', default='4:5', choices=list(KHUNG))
ap.add_argument('--ra', required=True)
ap.add_argument('--model', default='klein-4b', choices=list(MODEL))
ap.add_argument('--cong', default='', help='địa chỉ cổng wrangler dev, vd http://127.0.0.1:8841')
a = ap.parse_args()
if len(a.mau) > 4: sys.exit('Tối đa 4 ảnh mẫu.')

# Ảnh mẫu: thu cạnh dài về 1024 (đỡ neuron), gửi JPEG; ảnh trong suốt lót nền trắng.
mau = []
for p in a.mau:
    im = ImageOps.exif_transpose(Image.open(p))  # ảnh chụp điện thoại: xoay đúng chiều
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); nen = Image.new('RGB', im.size, 'white'); nen.paste(im, mask=im.split()[3]); im = nen
    im = im.convert('RGB'); im.thumbnail((1024, 1024))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=92); mau.append((b.getvalue(), im.size))
w, h = KHUNG[a.ti_le]
can = round(uoc_neuron(w, h, [s for _, s in mau]))

thu_muc = os.path.dirname(os.path.abspath(a.ra)); os.makedirs(thu_muc, exist_ok=True)
so = os.path.join(thu_muc, 'so-chi.jsonl')
hom_nay = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
da_dung = 0
if os.path.exists(so):
    for dong in open(so, encoding='utf-8'):
        try:
            d = json.loads(dong)
            if d.get('ngay_utc') == hom_nay and d.get('ok'): da_dung += d.get('neuron', 0)
        except ValueError:
            pass
if da_dung + can > MIEN_PHI_NGAY:
    sys.exit(f'DỪNG: hôm nay (giờ UTC) sổ này đã dùng ~{da_dung} neuron, lượt này cần ~{can} ⇒ vượt {MIEN_PHI_NGAY} miễn phí. '
             'Chờ sang ngày (7h sáng giờ Việt Nam). Sổ chỉ đếm thư mục này; '
             'việc khác dùng Workers AI cùng tài khoản cũng ăn vào mức miễn phí.')

ranh = '----anhqc' + uuid.uuid4().hex
than = io.BytesIO()
def truong(ten, gia_tri, la_anh=False):
    than.write(f'--{ranh}\r\n'.encode())
    if la_anh:
        than.write(f'Content-Disposition: form-data; name="{ten}"; filename="{ten}.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode())
        than.write(gia_tri)
    else:
        than.write(f'Content-Disposition: form-data; name="{ten}"\r\n\r\n{gia_tri}'.encode())
    than.write(b'\r\n')
truong('prompt', open(a.loi_nho, encoding='utf-8').read())
truong('width', str(w)); truong('height', str(h))
for i, (b, _) in enumerate(mau): truong(f'input_image_{i}', b, True)
than.write(f'--{ranh}--\r\n'.encode())
kieu = f'multipart/form-data; boundary={ranh}'

token = ''
if a.cong:
    if not re.fullmatch(r'http://(127\.0\.0\.1|localhost):\d{2,5}', a.cong.rstrip('/')): sys.exit('--cong chỉ nhận http://127.0.0.1:<cổng>')
    req = urllib.request.Request(a.cong.rstrip('/') + '/ve?model=' + MODEL[a.model], data=than.getvalue(),
                                 headers={'Content-Type': kieu, 'X-Anh-QC': '1'}, method='POST')  # cổng chỉ nhận lời gọi có dấu này
else:
    tk, token = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '').strip(), os.environ.get('CLOUDFLARE_API_TOKEN', '').strip()
    if not tk or not token:
        sys.exit('THIẾU: đặt CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN (token mẫu "Workers AI" ở dash.cloudflare.com), '
                 'hoặc chạy cổng wrangler dev rồi thêm --cong. Không dán token vào chat.')
    if not re.fullmatch(r'[0-9a-f]{32}', tk): sys.exit('CLOUDFLARE_ACCOUNT_ID phải là 32 ký tự 0-9a-f.')
    req = urllib.request.Request(f'https://api.cloudflare.com/client/v4/accounts/{tk}/ai/run/{MODEL[a.model]}',
                                 data=than.getvalue(), headers={'Content-Type': kieu, 'Authorization': f'Bearer {token}'},
                                 method='POST')

t = time.time(); ok = False; loi = ''
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        dl = r.read()
    if a.cong:
        anh = dl
    else:
        j = json.loads(dl); anh = base64.b64decode(((j.get('result') or {}).get('image')) or '')
    if anh:
        Image.open(io.BytesIO(anh)).save(a.ra); ok = True
    else:
        loi = 'không có ảnh trong phản hồi'
except urllib.error.HTTPError as e:
    loi = f'HTTP {e.code}: ' + e.read()[:300].decode('utf-8', 'ignore')
except Exception as e:
    loi = str(e)[:300]
if token: loi = loi.replace(token, '***')
with open(so, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'luc': time.strftime('%Y-%m-%d %H:%M:%S'), 'ngay_utc': hom_nay, 'model': MODEL[a.model],
                        'khung': f'{w}x{h}', 'ra': a.ra, 'ok': ok, 'usd': 0, 'neuron': can if ok else 0,
                        'giay': round(time.time() - t), 'loi': loi}, ensure_ascii=False) + '\n')
print(f'OK {a.ra} · {w}x{h} · ~{can} neuron · hôm nay ~{da_dung + can}/{MIEN_PHI_NGAY} miễn phí' if ok else 'LỖI ' + loi)
