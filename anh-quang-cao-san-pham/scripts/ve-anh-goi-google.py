# Vẽ 1 ảnh bằng GÓI Google AI Pro qua Antigravity CLI (`agy` → công cụ generate_image) — 0đ thêm, trừ vào trần tuần riêng của gói.
# Cần: cài Antigravity CLI (lệnh `agy`) + đăng nhập Gmail có gói. Máy gọi `agy -p` trong thư mục tạm TRỐNG (đã chép ảnh mẫu vào),
# lấy conversation_id, chờ ảnh ra ở ~/.gemini/antigravity-cli/brain/<id>/ và đứng yên 45 giây (agy hay vẽ 2–3 bản) → lấy bản mới nhất.
# Hết lượt / agy báo lỗi (status khác SUCCESS) → dừng ngay, in "LỖI …", thoát mã 1. Ảnh lưu ĐÚNG tên --ra (đổi định dạng nếu cần). Mỗi lần chạy ghi 1 dòng vào so-chi.jsonl cạnh --ra.
# Chạy: python ve-anh-goi-google.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.jpg anh-hang/b.jpg --ti-le 4:5 --ra ve/canh-1-a.png
#       [--cho 600]  (đổi lệnh agy bằng biến môi trường AGY=đường dẫn)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, glob, io, json, os, re, shutil, subprocess, sys, tempfile, time
from PIL import Image

KHUNG = {'1:1': '1:1 square', '4:5': '4:5 vertical', '9:16': '9:16 tall vertical', '16:9': '16:9 wide horizontal'}
DAU = ('The reference images show one REAL product from different angles. Keep that product EXACTLY identical: '
       'same shape, proportions, colors, logo, label text and every small detail. Do not redesign it. '
       'Place it into this advertising scene: ')
BRAIN = os.path.expanduser('~/.gemini/antigravity-cli/brain')

def luu_dung_ten(buf, ra):  # lưu ĐÚNG tên --ra (máy soát sau trỏ đúng tệp này); khác định dạng thì đổi bằng Pillow
    dang = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}.get(os.path.splitext(ra)[1].lower())
    im = Image.open(io.BytesIO(buf))
    if im.format == dang:
        with open(ra, 'wb') as f: f.write(buf)
    else: im.convert('RGB').save(ra, dang or 'PNG')
ap = argparse.ArgumentParser(description='Vẽ ảnh bằng gói Google AI Pro qua Antigravity CLI (0đ thêm)')
ap.add_argument('--loi-nho', required=True)
ap.add_argument('--mau', nargs='*', default=[], help='tối đa 3 ảnh mẫu chính hãng')
ap.add_argument('--ti-le', default='4:5', choices=list(KHUNG))
ap.add_argument('--ra', required=True)
ap.add_argument('--cho', type=int, default=600, help='giây chờ tối đa')
a = ap.parse_args()
if len(a.mau) > 3: sys.exit('Tối đa 3 ảnh mẫu.')
agy = os.environ.get('AGY') or shutil.which('agy') or next((p for p in (os.path.expanduser('~/.local/bin/agy'),
      os.path.join(os.environ.get('LOCALAPPDATA', ''), 'agy', 'bin', 'agy.exe')) if os.path.exists(p)), os.path.expanduser('~/.local/bin/agy'))
if not os.path.exists(agy): sys.exit('LỖI chưa cài Antigravity CLI (lệnh agy) — chạy scripts/kiem-cong-cu-ve.py, làm theo dòng đường gói Google.')

os.makedirs(os.path.dirname(os.path.abspath(a.ra)) or '.', exist_ok=True)
t0 = time.time(); ok = False; loi_bao = ''; ra = a.ra
with tempfile.TemporaryDirectory() as tam:  # thư mục trống: agy không thấy kho nào của bạn
    ten = []
    for i, p in enumerate(a.mau, 1):
        ten.append(f'mau-{i}' + (os.path.splitext(p)[1].lower() or '.jpg')); shutil.copy(p, os.path.join(tam, ten[-1]))
    nho = (' '.join('@' + t for t in ten) + f' Generate ONE {KHUNG[a.ti_le]} image with the generate_image tool (do not run any shell command, '
           'do not write any file yourself). Pass ALL attached files as image references. '
           + (DAU if ten else '') + open(a.loi_nho, encoding='utf-8').read().strip()).strip()
    try:
        r = subprocess.run([agy, '-p', nho, '--model', 'gemini-3.8-flash-medium', '--output-format', 'json', '--print-timeout', '420s'],
                           cwd=tam, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=a.cho)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired as e:  # agy hay in xong JSON mà không thoát (#1313) → vẫn đọc chữ đã in
        out = ''.join(x.decode('utf-8', 'ignore') if isinstance(x, bytes) else (x or '') for x in (e.stdout, e.stderr))
    d = {}
    for dong in reversed(out.strip().splitlines()):  # agy in 1 dòng JSON {status, error, conversation_id…}
        try: d = json.loads(dong); break
        except ValueError: pass
    d = d if isinstance(d, dict) else {}
    if 'RESOURCE_EXHAUSTED' in out or 'quota reached' in out.lower():
        loi_bao = ('hết lượt gói Google: ' + str(d.get('error') or 'trần tuần vẽ ảnh'))[:200]
    elif d.get('status') and d['status'] != 'SUCCESS':
        loi_bao = f"agy báo lỗi {d['status']}: {d.get('error', '')}"[:200]
    else:
        m = re.search(r'"conversation_id"\s*:\s*"([0-9a-f-]{36})"', out) or re.search(r'brain/([0-9a-f-]{36})', out)
        if not m: loi_bao = ('không thấy conversation_id: ' + out[-200:].replace('\n', ' ')).strip()
        else:
            anh, yen = [], 0
            while time.time() - t0 < a.cho + 300:  # sau lệnh agy còn chờ ảnh ra tối đa thêm 5 phút
                moi = glob.glob(f'{BRAIN}/{m.group(1)}/*.jpg') + glob.glob(f'{BRAIN}/{m.group(1)}/*.png')
                yen = yen + 1 if moi and len(moi) == len(anh) else 0
                anh = moi
                if yen >= 9: break  # đứng yên 9×5 = 45 giây
                time.sleep(5)
            if anh:
                with open(max(anh, key=os.path.getmtime), 'rb') as f: luu_dung_ten(f.read(), ra)
                ok = True
            else: loi_bao = 'agy chạy xong nhưng không ra ảnh'
giay = round(time.time() - t0)
so = os.path.join(os.path.dirname(os.path.abspath(a.ra)), 'so-chi.jsonl')
with open(so, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'luc': time.strftime('%Y-%m-%d %H:%M:%S'), 'duong': 'goi-google', 'ti_le': a.ti_le, 'ra': ra, 'ok': ok,
                        'usd': 0, 'giay': giay, 'loi': loi_bao}, ensure_ascii=False) + '\n')
print(f'OK {ra} · {giay} giây · 0đ (trừ trần tuần gói Google)' if ok else f'LỖI {loi_bao} · {giay} giây')
if not ok: sys.exit(1)
