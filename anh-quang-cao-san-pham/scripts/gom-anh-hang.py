# Gom ảnh chính hãng từ 1 trang sản phẩm: tải mọi ảnh trên trang, giữ ảnh cạnh ngắn ≥ 500px (bỏ icon),
# lưu PNG đánh số vào <thư mục>/tho/ và ghép 1 bảng xem nhanh có số (bang-xem.jpg) để chọn ảnh dùng.
# Chạy: python gom-anh-hang.py "https://trang-hang/san-pham" anh-hang [toi_thieu=500] [--them-ten-mien cdn.hang.com,...] [--chi-bang-xem]
#   --chi-bang-xem  không tải gì: chỉ dựng bang-xem.jpg + nguon.txt từ ảnh bạn TỰ LƯU vào <thư mục>/tho/ (đánh số lại 01, 02…)
# Máy tự xưng là máy (không giả trình duyệt). Trang chặn máy (401/403/429/503, trang thử thách/captcha) → máy dừng và
# hướng dẫn tự lưu ảnh bằng trình duyệt rồi chạy lại với --chi-bang-xem. Không vượt chặn.
# Đọc được ảnh nạp chậm (data-lazy-src, data-zoom-image…), ảnh nằm trong JSON/script; link có dấu cách/tiếng Việt/ngoặc được mã hoá;
# cùng 1 ảnh khác cỡ của kho ảnh (-300x300, _large, ?w=200…) chỉ tải 1 bản (bản lớn nhất).
# An toàn: chỉ tải ảnh CÙNG tên miền với trang (kho ảnh/CDN của hãng thêm bằng --them-ten-mien), chặn địa chỉ
# mạng nội bộ / localhost kể cả khi bị chuyển hướng, bỏ ảnh quá 40 triệu điểm ảnh.
# Ảnh tải về là dữ liệu không tin cậy: chỉ mở bằng Pillow, không chạy gì từ đó. Chỉ dùng trang của hãng / đại lý chính thức.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import html, io, ipaddress, os, re, socket, sys, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageOps

Image.MAX_IMAGE_PIXELS = 40_000_000
args = sys.argv[1:]; them = []; chi_bang = '--chi-bang-xem' in args
if chi_bang: args.remove('--chi-bang-xem')
if '--them-ten-mien' in args:
    i = args.index('--them-ten-mien')
    if i + 1 >= len(args): sys.exit('Thiếu tên miền sau --them-ten-mien')
    them = [t.strip().lower() for t in args[i + 1].split(',') if t.strip()]; del args[i:i + 2]
if len(args) < 2: sys.exit('Cách chạy: python gom-anh-hang.py "<link trang sản phẩm>" <thư mục> [toi_thieu=500] [--them-ten-mien a.com,b.com] [--chi-bang-xem]')
url, ra = args[0], args[1]; toi_thieu = int(args[2]) if len(args) > 2 else 500
if not url.startswith(('http://', 'https://')): sys.exit('Link phải bắt đầu bằng http(s)://')
UA = {'User-Agent': 'anh-quang-cao-san-pham/1.1 (+gom anh san pham cho nguoi ban hang)'}
tho = os.path.join(ra, 'tho')

def host(u): return (urllib.parse.urlsplit(u).hostname or '').lower()
def goc(h):  # tên miền gốc: shop.hang.vn → hang.vn · www.hang.com.vn → hang.com.vn
    p = h.split('.')
    return '.'.join(p[-3:] if len(p) >= 3 and p[-2] in ('com', 'net', 'org', 'co', 'edu', 'gov') else p[-2:])
GOC = goc(host(url))
def dung_mien(u):
    h = host(u)
    return goc(h) == GOC or any(h == t or h.endswith('.' + t) for t in them)
def ma_hoa(u):  # link có dấu cách / tiếng Việt / ngoặc → mã hoá đường dẫn + truy vấn, giữ nguyên %XX đã có
    s = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((s.scheme, s.netloc, urllib.parse.quote(s.path, safe="/%:@!$&'*+,;=~-._"),
                                    urllib.parse.quote(s.query, safe="/%:@!$&'*+,;=~-._?"), ''))
def an_toan(u):  # chỉ địa chỉ Internet công khai, chặn localhost / mạng nội bộ
    s = urllib.parse.urlsplit(u)
    if s.scheme not in ('http', 'https') or not s.hostname: return False
    try: ips = {a[4][0] for a in socket.getaddrinfo(s.hostname, None)}
    except OSError: return False
    return bool(ips) and all(ipaddress.ip_address(ip.split('%')[0]).is_global for ip in ips)
class ChanChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not an_toan(newurl): raise urllib.error.URLError('bị chuyển hướng tới địa chỉ nội bộ')
        return super().redirect_request(req, fp, code, msg, headers, newurl)
mo = urllib.request.build_opener(ChanChuyenHuong)
def tai(u, toi_da=15_000_000):
    u = ma_hoa(u)
    if not an_toan(u): raise ValueError('địa chỉ nội bộ / không phân giải được')
    with mo.open(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return r.read(toi_da + 1)

def thoat_bi_chan(ly_do):
    sys.exit(f'Trang này không cho máy lấy ảnh ({ly_do}). Máy không cố vượt chặn. Bạn làm tay như sau:\n'
             f'  1) Mở trang bằng trình duyệt: {url}\n'
             f'  2) Bấm chuột phải vào từng ảnh sản phẩm → "Lưu ảnh thành…" → lưu vào thư mục: {os.path.abspath(tho)}\n'
             f'  3) Chạy lại đúng lệnh cũ, thêm --chi-bang-xem ở cuối — máy sẽ đánh số ảnh và dựng bang-xem.jpg.')

def luu(im, u, giu, da_giu):  # lọc cỡ + trùng theo dấu ảnh, lưu PNG đánh số; trả True nếu giữ
    if min(im.size) < toi_thieu: return False
    im = ImageOps.exif_transpose(im)  # ảnh chụp điện thoại: xoay đúng chiều theo thẻ EXIF
    if 'A' in im.getbands() or im.mode == 'P':  # ảnh nền trong suốt: đặt lên nền trắng rồi mới lấy dấu (không thì mọi ảnh trong suốt giống nhau)
        im = im.convert('RGBA'); nen = Image.new('RGBA', im.size, 'white'); nen.alpha_composite(im); hinh = nen.convert('RGB')
    else: hinh = im
    g = list(hinh.convert('L').resize((16, 16)).tobytes()); tb = sum(g) / 256  # dấu ảnh gần đúng: cùng ảnh khác link/nén → bỏ
    dau = sum(1 << i for i, v in enumerate(g) if v > tb)
    mau = hinh.convert('RGB').resize((4, 4)).tobytes()  # dấu màu thô: cùng góc chụp nhưng KHÁC MÀU (đỏ/navy) không phải ảnh trùng
    if any(bin(dau ^ d).count('1') <= 10 and sum(abs(x - y) for x, y in zip(mau, m)) / len(mau) <= 16 for d, m in da_giu): return False
    da_giu.append((dau, mau))
    p = os.path.join(tho, f'{len(giu) + 1:02d}.png'); im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB').save(p)
    giu.append((p, u, im.size)); return True

def khoa_anh(u):  # khoá chuẩn hoá: bỏ đuôi cỡ / tham số cỡ → cùng ảnh khác cỡ ra cùng khoá; trả (khoá, điểm cỡ: cao = bản lớn, cạnh ngắn biết trước)
    s = urllib.parse.urlsplit(u); duong, ext = os.path.splitext(s.path); diem = canh = 10 ** 9
    duong = re.sub(r'/cache/[0-9a-f]{32}/', '/cache/', duong)  # Magento: mã trong /cache/ chỉ là mã cỡ ảnh (cùng ảnh)
    m = re.search(r'/(?:thumb/|resized?/|crop/)?(\d{2,4})x(\d{2,4})/', duong)  # cỡ nằm ở thư mục: /thumb/150x100/…
    if m: duong = duong[:m.start()] + '/' + duong[m.end():]; diem, canh = int(m.group(1)) * int(m.group(2)), min(int(m.group(1)), int(m.group(2)))
    m = re.search(r'[-_](\d{2,4})x(\d{2,4})$', duong)
    if m: duong, diem, canh = duong[:m.start()], int(m.group(1)) * int(m.group(2)), min(int(m.group(1)), int(m.group(2)))
    else:
        m = re.search(r'[_-](pico|icon|thumb|small|compact|medium|large|grande|master)$', duong, re.I)
        if m:
            duong = duong[:m.start()]
            diem = {'pico': 16, 'icon': 32, 'thumb': 50, 'small': 100, 'compact': 160, 'medium': 240, 'large': 480, 'grande': 600, 'master': 10 ** 8}[m.group(1).lower()]
    giu_q = []
    for k, v in urllib.parse.parse_qsl(s.query, keep_blank_values=True):
        if k.lower() in ('w', 'h', 'width', 'height', 'size', 'resize', 'quality', 'q', 'fit', 'crop', 'dpr'):
            if k.lower() in ('w', 'width', 'size') and v.isdigit(): diem, canh = min(diem, int(v) ** 2), min(canh, int(v))
        else: giu_q.append((k, v))
    return (s.netloc.lower(), duong, tuple(giu_q)), diem, canh  # (bản .jpg/.webp cùng tên coi là 1 ảnh)

def dung_bang(giu, khac_bao=''):
    o = 260; cot = 6; hang = (len(giu) + cot - 1) // cot
    bang = Image.new('RGB', (cot * (o + 10) + 10, hang * (o + 40) + 10), 'white'); d = ImageDraw.Draw(bang)
    for i, (p, u, sz) in enumerate(giu):
        im = Image.open(p).convert('RGBA'); im.thumbnail((o, o))
        nen = Image.new('RGBA', im.size, 'white'); nen.alpha_composite(im); im = nen.convert('RGB')  # nền trong suốt hiện trắng, không đen
        x, y = 10 + (i % cot) * (o + 10), 10 + (i // cot) * (o + 40)
        bang.paste(im, (x, y)); d.text((x, y + o + 4), f'{i + 1:02d}  {sz[0]}x{sz[1]}', fill=(0, 0, 0))
    bang.save(os.path.join(ra, 'bang-xem.jpg'), quality=85)
    with open(os.path.join(ra, 'nguon.txt'), 'w', encoding='utf-8') as f:
        f.writelines(f'{os.path.basename(p)}\t{sz[0]}x{sz[1]}\t{u}\n' for p, u, sz in giu)
    print(f'ok {len(giu)} ảnh → {tho} · xem nhanh: {ra}/bang-xem.jpg · nguồn: {ra}/nguon.txt' + (f'\n{khac_bao}' if khac_bao else ''))

os.makedirs(tho, exist_ok=True)
giu, da_giu = [], []
if chi_bang:  # chỉ dựng bảng từ ảnh người dùng tự lưu; đọc hết vào bộ nhớ trước rồi mới ghi PNG đánh số
    cho = []
    for ten in sorted(os.listdir(tho)):
        if not re.search(r'\.(jpe?g|png|webp|gif|bmp)$', ten, re.I): continue
        try:
            im = Image.open(os.path.join(tho, ten)); im.load(); cho.append((ten, im))
        except Exception: continue
    for ten, im in cho: luu(im, 'tải tay ← ' + ten, giu, da_giu)
    if not giu: sys.exit(f'Không có ảnh nào ≥ {toi_thieu}px trong {tho}. Hãy lưu ảnh sản phẩm vào đó rồi chạy lại.')
    dung_bang(giu)
    sys.exit(0)

try:
    trang = tai(url).decode('utf-8', 'ignore')
except urllib.error.HTTPError as e:
    if e.code in (401, 403, 429, 503): thoat_bi_chan(f'HTTP {e.code}')
    sys.exit(f'Không mở được trang: HTTP {e.code}')
except Exception as e:
    sys.exit(f'Không mở được trang: {e}')
dau_chan = [m for m in ('cf-chl', 'captcha', 'access denied') if m in trang.lower()]
trang = html.unescape(trang).replace('\\/', '/').replace('\\u002F', '/').replace('\\u002f', '/').replace('\\u0026', '&')
EXT = r'\.(?:jpe?g|png|webp)'
lien = re.findall(r'["\'(]([^"\'()\s<>]*?' + EXT + r'(?:\?[^"\'\s<>]*)?)["\')]', trang, re.I)  # mọi chuỗi trong ngoặc kép/đơn: src, data-lazy-src, data-zoom-image, JSON "full", poster, url(…)
lien += re.findall(r'["\']([^"\'\s<>]*?(?:\([^"\'\s<>]*\))[^"\'\s<>]*?' + EXT + r')["\']', trang, re.I)  # tên có ngoặc: 0(192).png
lien += [u.split()[0] for s in re.findall(r'(?:data-)?srcset=["\']([^"\']+)["\']', trang, re.I) for u in s.split(',') if u.strip()]
nhom, khac, thu_tu = {}, {}, []  # khoá chuẩn hoá → [(điểm, link)] · tên miền khác → số ảnh
for u in lien:
    u = urllib.parse.urljoin(url, u.strip())
    if not u.startswith(('http://', 'https://')): continue
    if not dung_mien(u):
        khac[host(u)] = khac.get(host(u), 0) + 1; continue
    k, diem, canh = khoa_anh(u)
    if k not in nhom: nhom[k] = []; thu_tu.append(k)
    if all(u != x[1] for x in nhom[k]): nhom[k].append((diem, u, canh))
thu_tu = [k for k in thu_tu if any(c >= toi_thieu for _, _, c in nhom[k])]  # bỏ nhóm mà MỌI bản đều biết trước là ảnh nhỏ (icon, thumb)
bi_chan = 0
for k in thu_tu[:150]:
    if bi_chan: break
    for diem, u, _ in sorted(nhom[k], key=lambda x: -x[0]):  # bản lớn nhất trước; tải hỏng mới thử bản kế
        try:
            b = tai(u)
            if len(b) > 15_000_000: break
            im = Image.open(io.BytesIO(b))
            if im.width * im.height > 40_000_000: break  # ảnh "bom" giải nén
            im.load()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 429, 503) and not giu: thoat_bi_chan(f'ảnh trả HTTP {e.code}')
            if e.code in (429, 503): bi_chan = e.code; break  # trang bảo chậm lại ⇒ dừng hẳn, không gọi tiếp các ảnh khác
            continue
        except Exception:
            continue
        if min(im.size) < toi_thieu: continue  # bản nhỏ (cỡ chưa rõ từ link) → thử bản kế cùng nhóm
        luu(im, u, giu, da_giu); break
bao_khac = ''
if khac:
    bao_khac = ('Bỏ ảnh ở tên miền khác: ' + ', '.join(f'{h} ({n})' for h, n in sorted(khac.items(), key=lambda x: -x[1])[:8])
                + '. Tên nào là kho ảnh của chính hãng → chạy lại kèm --them-ten-mien <tên>.')
if not giu:
    if dau_chan: thoat_bi_chan('thân trang có dấu thử thách/captcha: ' + ', '.join(dau_chan))
    sys.exit('Không lấy được ảnh nào ≥ %dpx (trang có thể nạp ảnh bằng JavaScript → tải tay: lưu ảnh vào %s rồi chạy lại với --chi-bang-xem). %s' % (toi_thieu, tho, bao_khac))
if bi_chan:
    bao_khac = (f'⚠️ Trang trả HTTP {bi_chan} (bảo máy chậm lại) ⇒ máy DỪNG, chỉ giữ {len(giu)} ảnh đã lấy. '
                'Thiếu góc nào thì lưu tay vào thư mục ảnh rồi chạy lại với --chi-bang-xem. ' + bao_khac)
dung_bang(giu, bao_khac)
