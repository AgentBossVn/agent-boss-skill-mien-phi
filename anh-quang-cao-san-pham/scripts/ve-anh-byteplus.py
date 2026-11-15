# Vẽ 1 ảnh bằng Seedream qua BytePlus ModelArk (200 ảnh miễn phí Seedream 4.5 mỗi tài khoản, hết thì trả tiền ~0,04 USD/ảnh).
# Khoá đọc theo thứ tự: biến ARK_API_KEY → tệp ~/.config/anh-qc/byteplus.key → (Mac) Keychain byteplus-ark-claude-thu-anh. KHÔNG in khoá.
# Ảnh mẫu xoay đúng chiều + thu nhỏ cạnh dài ≤1536px (JPEG 90) trước khi gửi. Trần tiền/ngày cộng ở 1 sổ chung ~/.config/anh-qc/so-chi-byteplus.jsonl
# (mọi thư mục dự án), vượt --tran-usd thì từ chối. Ảnh lưu ĐÚNG tên --ra (đổi định dạng nếu cần).
# Lỗi → in "LỖI …", thoát mã 1. Đo 15/11/2026: Seedream 4.5 ~30–60 giây/ảnh; hay vẽ SAI SỐ trên nhãn (336 g → 136 g) → luôn soát chữ.
# Chạy: ~/.venv-anh-qc/bin/python ve-anh-byteplus.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.jpg anh-hang/b.jpg --ti-le 4:5 --ra ve/canh-1.jpg
#       [--model seedream-4-5-251128] [--tran-usd 1]
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, base64, io, json, os, subprocess, sys, time
import requests
from PIL import Image, ImageOps

URL = 'https://ark.ap-southeast.bytepluses.com/api/v3/images/generations'
SIZE = {'4:5': '1920x2400', '9:16': '1440x2560', '16:9': '2560x1440', '1:1': '2048x2048'}
DAU = ('The reference images show one REAL product from different angles. Keep that product EXACTLY identical: '
       'same shape, proportions, colors, logo, label text and every small detail. Do not redesign it. '
       'Place it into this advertising scene: ')
ap = argparse.ArgumentParser(description='Vẽ ảnh bằng Seedream qua BytePlus ModelArk')
ap.add_argument('--loi-nho', required=True)
ap.add_argument('--mau', nargs='*', default=[], help='tối đa 3 ảnh mẫu chính hãng')
ap.add_argument('--ti-le', default='4:5', choices=list(SIZE))
ap.add_argument('--ra', required=True)
ap.add_argument('--model', default='seedream-4-5-251128')
ap.add_argument('--tran-usd', type=float, default=1.0, help='trần tiền/ngày cho đường này (USD)')
a = ap.parse_args()
if len(a.mau) > 3: sys.exit('Tối đa 3 ảnh mẫu.')


def lay_khoa():
    k = os.environ.get('ARK_API_KEY', '').strip()
    tep = os.path.expanduser('~/.config/anh-qc/byteplus.key')
    if not k and os.path.exists(tep): k = open(tep, encoding='utf-8-sig').read().strip()  # Notepad có thể lưu kèm BOM
    if not k and sys.platform == 'darwin':
        k = subprocess.run(['security', 'find-generic-password', '-s', 'byteplus-ark-claude-thu-anh', '-w'],
                           capture_output=True, text=True).stdout.strip()
    return k if len(k) >= 20 else ''

khoa = lay_khoa()
if not khoa: sys.exit('LỖI chưa có khoá BytePlus (đặt ARK_API_KEY hoặc tệp ~/.config/anh-qc/byteplus.key).')
usd = 0.036 if a.model.startswith('seedream-5') else 0.04  # giá niêm yết / ảnh (4.5 = 0,04 · 5.5 ≈ 0,036)
os.makedirs(os.path.dirname(os.path.abspath(a.ra)) or '.', exist_ok=True)
so = os.path.join(os.path.dirname(os.path.abspath(a.ra)), 'so-chi.jsonl')  # sổ của dự án (để xem lại)
so_tran = os.path.expanduser('~/.config/anh-qc/so-chi-byteplus.jsonl')  # sổ chung để tính trần ngày
os.makedirs(os.path.dirname(so_tran), mode=0o700, exist_ok=True)
homnay, da_chi = time.strftime('%Y-%m-%d'), 0.0
if os.path.exists(so_tran):
    for d in open(so_tran, encoding='utf-8'):
        try: j = json.loads(d)
        except ValueError: continue
        if j.get('duong') == 'byteplus' and str(j.get('luc', '')).startswith(homnay): da_chi += float(j.get('usd') or 0)
if da_chi + usd > a.tran_usd:
    sys.exit(f'LỖI chạm trần: hôm nay đã ~{da_chi:.2f} USD, thêm ảnh này {usd} USD vượt --tran-usd {a.tran_usd}.')


def nho(p):  # thu nhỏ cạnh dài ≤1536px → JPEG 90 → data URI
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB'); im.thumbnail((1536, 1536), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=90)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

def luu_dung_ten(buf, ra):  # lưu ĐÚNG tên --ra (máy soát sau trỏ đúng tệp này); khác định dạng thì đổi bằng Pillow
    dang = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}.get(os.path.splitext(ra)[1].lower())
    im = Image.open(io.BytesIO(buf))
    if im.format == dang:
        with open(ra, 'wb') as f: f.write(buf)
    else: im.convert('RGB').save(ra, dang or 'PNG')

loi = (DAU if a.mau else '') + open(a.loi_nho, encoding='utf-8').read().strip()
vao = {'model': a.model, 'prompt': loi, 'size': SIZE[a.ti_le], 'sequential_image_generation': 'disabled',
       'response_format': 'b64_json', 'watermark': False}
if a.mau: vao['image'] = [nho(p) for p in a.mau]
t0 = time.time(); ok = False; loi_bao = ''; ra = a.ra
try:
    r = requests.post(URL, json=vao, headers={'Authorization': f'Bearer {khoa}'}, timeout=300)
    try: j = r.json()
    except ValueError: j = {'error': {'message': r.text[:200]}}
    if r.ok and j.get('data') and j['data'][0].get('b64_json'):
        buf = base64.b64decode(j['data'][0]['b64_json'])
        luu_dung_ten(buf, ra)
        ok = True
    else:
        e = j.get('error', j) if isinstance(j, dict) else j
        loi_bao = f'HTTP {r.status_code}: ' + (str(e.get('message', e)) if isinstance(e, dict) else str(e))[:300]
except requests.RequestException as e:
    loi_bao = type(e).__name__ + ' (lỗi mạng)'
giay = round(time.time() - t0)
dong = json.dumps({'luc': time.strftime('%Y-%m-%d %H:%M:%S'), 'duong': 'byteplus', 'model': a.model, 'ti_le': a.ti_le, 'ra': os.path.abspath(ra),
                   'ok': ok, 'usd': usd if ok else 0, 'giay': giay, 'loi': loi_bao}, ensure_ascii=False) + '\n'
for p in (so, so_tran):
    with open(p, 'a', encoding='utf-8') as f: f.write(dong)
print(f'OK {ra} · {giay} giây · ~{usd} USD (tính trần; còn lượt miễn phí thì không trừ tiền)' if ok else f'LỖI {loi_bao} · {giay} giây')
if not ok: sys.exit(1)
