#!/usr/bin/env python3
"""Lấy màu + font của một thương hiệu từ trang web, tệp .svg / .png / .css / .html.

Chạy:  python lay-mau.py <nguồn> [<nguồn> ...] [--json]
  nguồn = URL (https://...), hoặc đường dẫn tệp .svg .png .css .html
In: bảng màu hay gặp nhất (hex, số lần hoặc tỉ lệ điểm ảnh), nhóm "màu trung tính" (trắng/đen/xám) riêng,
    và với web/HTML/CSS: font-family + font Google Fonts tìm thấy. --json: in JSON cho máy đọc.
Chỉ thư viện chuẩn. PNG tự giải mã (8-bit, không xen kẽ); JPG/WEBP không đọc được.
"""
import sys, re, json, zlib, struct, argparse
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote, parse_qs
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HEX_RE = re.compile(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])')
RGB_RE = re.compile(r'rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})')
FONT_RE = re.compile(r'font-family\s*:\s*([^;}{]+)', re.I)
LINK_CSS_RE = re.compile(r'<link\b[^>]*>', re.I)
TOP = 8


class Loi(Exception):
    pass


def hex_tu_rgb(r, g, b): return '#%02X%02X%02X' % (r, g, b)


def la_trung_tinh(r, g, b): return max(r, g, b) - min(r, g, b) < 16  # trắng / đen / xám


def dem_mau_trong_chu(text: str) -> Counter:
    c = Counter()
    for m in HEX_RE.finditer(text):
        h = m.group(1)
        if len(h) == 3: h = ''.join(ch * 2 for ch in h)
        c['#' + h[:6].upper()] += 1
    for m in RGB_RE.finditer(text):
        r, g, b = (min(255, int(x)) for x in m.groups())
        c[hex_tu_rgb(r, g, b)] += 1
    return c


def vung_css(html: str) -> str:
    """Chỉ phần CSS của trang HTML: nội dung <style> và thuộc tính style="..." (không quét cả trang: &#039; hay href="#fab" không phải màu)."""
    kq = [m.group(1) for m in re.finditer(r'<style\b[^>]*>(.*?)</style>', html, re.S | re.I)]
    kq += [m.group(2) for m in re.finditer(r'\sstyle\s*=\s*(["\'])(.*?)\1', html, re.S | re.I)]
    return '\n'.join(kq)


def tach_font(text: str, gg_text: str = None):
    """(danh sách font-family dùng, danh sách font Google Fonts). gg_text: chữ để tìm link Google Fonts (mặc định = text)"""
    dung = Counter()
    for m in FONT_RE.finditer(text):
        ho = m.group(1).split(',')[0].strip().strip('\'"')
        if ho and not ho.lower().startswith(('var(', 'inherit', 'initial')) and ho.lower() not in ('sans-serif', 'serif', 'monospace', 'system-ui') and not re.search(r'awesome|icon|symbol|glyph|dashicons', ho, re.I):
            dung[ho] += 1
    gg = []
    for m in re.finditer(r'fonts\.googleapis\.com/css2?\?([^"\')\s>]+)', text if gg_text is None else gg_text):
        q = parse_qs(unquote(m.group(1).replace('&amp;', '&')))
        for f in q.get('family', []):
            ten = f.split(':')[0].replace('+', ' ').strip()
            if ten and ten not in gg: gg.append(ten)
    return [t for t, _ in dung.most_common(6)], gg


def tai(url: str) -> str:
    req = Request(url, headers={'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'})
    with urlopen(req, timeout=20) as r:
        raw = r.read(5_000_000)
        cs = r.headers.get_content_charset() or 'utf-8'
    return raw.decode(cs, 'replace')


# ---------------------------------------------------------------- PNG
def giai_ma_png(data: bytes):
    """Trả (rộng, cao, danh sách điểm (r,g,b,a) lấy mẫu). Ném Loi nếu không đọc được."""
    if data[:8] != b'\x89PNG\r\n\x1a\n': raise Loi('không phải tệp PNG')
    pos, ihdr, idat, plte, trns, iccp = 8, None, [], b'', b'', False
    while pos + 8 <= len(data):
        n, kieu = struct.unpack('>I4s', data[pos:pos + 8]); body = data[pos + 8:pos + 8 + n]; pos += 12 + n
        if kieu == b'IHDR': ihdr = struct.unpack('>IIBBBBB', body)
        elif kieu == b'IDAT': idat.append(body)
        elif kieu == b'PLTE': plte = body
        elif kieu == b'tRNS': trns = body
        elif kieu == b'iCCP': iccp = True
        elif kieu == b'IEND': break
    if not ihdr or not idat: raise Loi('PNG hỏng')
    w, h, depth, ct, _, _, inter = ihdr
    if inter or depth != 8 or ct not in (0, 2, 3, 4, 6):
        raise Loi('kiểu PNG này (xen kẽ / không phải 8-bit) máy không đọc được — mở ảnh xem bằng mắt, hoặc xuất lại PNG 8-bit thường / SVG')
    kenh = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]; dong = w * kenh
    if h * (dong + 1) > 110_000_000:  # đo: ~0,4 giây / 10 triệu byte ở trường hợp lọc chậm nhất → 110 triệu ≈ 45 giây
        raise Loi('ảnh quá lớn (giải nén >110 MB) — chụp lại không phải Retina, thu nhỏ ảnh, hoặc dùng SVG/web để lấy màu')
    if h * (dong + 1) > 30_000_000: print('(ảnh lớn, đọc có thể mất vài chục giây…)', file=sys.stderr)
    raw = zlib.decompress(b''.join(idat))
    if len(raw) < h * (dong + 1): raise Loi('PNG thiếu dữ liệu')
    buoc = max(1, int((w * h / 250_000) ** 0.5))  # lấy mẫu thưa theo hàng/cột: ~250 nghìn điểm (vẫn phải giải lọc mọi hàng vì lọc PNG phụ thuộc hàng trước)
    truoc = bytearray(dong); diem = []; p = 0
    for y in range(h):
        f = raw[p]; cur = bytearray(raw[p + 1:p + 1 + dong]); p += 1 + dong
        if f == 1:
            for i in range(kenh, dong): cur[i] = (cur[i] + cur[i - kenh]) & 255
        elif f == 2:
            for i in range(dong): cur[i] = (cur[i] + truoc[i]) & 255
        elif f == 3:
            for i in range(dong): cur[i] = (cur[i] + (((cur[i - kenh] if i >= kenh else 0) + truoc[i]) >> 1)) & 255
        elif f == 4:
            for i in range(dong):
                a = cur[i - kenh] if i >= kenh else 0; b = truoc[i]; c = truoc[i - kenh] if i >= kenh else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        elif f != 0: raise Loi('PNG hỏng (bộ lọc lạ)')
        truoc = cur
        if y % buoc: continue
        d = cur
        for x in range(0, w, buoc):
            i = x * kenh
            if ct == 6: diem.append((d[i], d[i + 1], d[i + 2], d[i + 3]))
            elif ct == 2: diem.append((d[i], d[i + 1], d[i + 2], 255))
            elif ct == 0: diem.append((d[i], d[i], d[i], 255))
            elif ct == 4: diem.append((d[i], d[i], d[i], d[i + 1]))
            else:
                k = d[i]; a = trns[k] if k < len(trns) else 255
                diem.append((plte[3 * k], plte[3 * k + 1], plte[3 * k + 2], a))
    return w, h, diem, iccp


def mau_tu_diem(diem):
    """Gom màu: lượng tử hóa 4 bit/kênh, lấy trung bình nhóm. Trả [(hex, số điểm)], tổng điểm đục."""
    nhom = {}
    tong = 0
    for r, g, b, a in diem:
        if a < 128: continue
        tong += 1
        k = (r >> 4, g >> 4, b >> 4); s = nhom.get(k)
        if s is None: nhom[k] = [r, g, b, 1]
        else: s[0] += r; s[1] += g; s[2] += b; s[3] += 1
    return [(hex_tu_rgb(s[0] // s[3], s[1] // s[3], s[2] // s[3]), s[3]) for s in nhom.values()], tong


# ---------------------------------------------------------------- phân tích 1 nguồn
def chia_nhom(cac_mau, tong, la_diem):
    """cac_mau: [(hex, đếm)] → (có màu, trung tính), mỗi mục {hex, dem, ti_le}"""
    co, tt = [], []
    for hx, n in sorted(cac_mau, key=lambda t: -t[1]):
        r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
        muc = {'hex': hx, 'dem': n, 'ti_le': round(n / tong, 4) if tong else 0}
        (tt if la_trung_tinh(r, g, b) else co).append(muc)
    return co[:TOP], tt[:3]


def phan_tich_chu(text: str, nguon: str, loai: str, them_css: str = ''):
    css = (vung_css(text) if loai in ('web', 'html', 'htm') else text) + '\n' + them_css
    c = dem_mau_trong_chu(css)
    tong = sum(c.values())
    co, tt = chia_nhom(list(c.items()), tong, False)
    dung, gg = tach_font(css, text + '\n' + them_css)
    return {'nguon': nguon, 'loai': loai, 'mau': co, 'trung_tinh': tt, 'font': dung, 'google_fonts': gg, 'ghi_chu': []}


def phan_tich(nguon: str):
    if re.match(r'https?://', nguon, re.I):
        html = tai(nguon); ghi = []
        css, da = '', 0
        for tag in LINK_CSS_RE.findall(html):
            if 'stylesheet' not in tag.lower(): continue
            m = re.search(r'href\s*=\s*["\']([^"\']+)', tag, re.I)
            if not m or 'fonts.googleapis.com' in m.group(1): continue
            if da >= 8: ghi.append('chỉ đọc 8 tệp CSS đầu'); break
            u = urljoin(nguon, m.group(1).replace('&amp;', '&'))
            if urlparse(u).scheme not in ('http', 'https'): continue
            da += 1
            try: css += '\n' + tai(u)
            except Exception as e: ghi.append(f'không tải được {u}: {e}')
        r = phan_tich_chu(html, nguon, 'web', css); r['ghi_chu'] = ghi
        if not r['mau'] and not r['trung_tinh']: r['ghi_chu'].append('không thấy màu trong HTML/CSS (trang dựng bằng JavaScript?) — chụp màn hình rồi đưa ảnh PNG')
        return r
    p = Path(nguon).expanduser()
    if not p.is_file(): raise Loi('không thấy tệp')
    ext = p.suffix.lower()
    if ext in ('.svg', '.css', '.html', '.htm'):
        return phan_tich_chu(p.read_text(encoding='utf-8', errors='replace'), str(p), ext[1:])
    if ext == '.png':
        w, h, diem, iccp = giai_ma_png(p.read_bytes())
        cac, tong = mau_tu_diem(diem)
        co, tt = chia_nhom(cac, tong, True)
        return {'nguon': str(p), 'loai': 'png', 'mau': co, 'trung_tinh': tt, 'font': [], 'google_fonts': [], 'ghi_chu': [f'ảnh {w}×{h}, tỉ lệ = phần điểm ảnh đục'] + (['màu có thể lệch do hồ sơ màu màn hình, ưu tiên lấy màu từ web/SVG/CSS'] if iccp else [])}
    if ext in ('.jpg', '.jpeg', '.webp', '.gif'):
        raise Loi(f'không đọc được {ext} — xuất lại thành PNG hoặc SVG, hoặc Agent tự mở ảnh xem bằng mắt')
    raise Loi('kiểu tệp không hỗ trợ (dùng URL, .svg, .png, .css, .html)')


def in_bang(r):
    print(f'\n== {r["nguon"]}  ({r["loai"]})')
    if r['mau']:
        print('| Màu | Số lần / tỉ lệ |\n|---|---|')
        for m in r['mau']:
            v = f'{m["ti_le"] * 100:.1f}%'.replace('.', ',') if r['loai'] == 'png' else f'{m["dem"]} lần'
            print(f'| {m["hex"]} | {v} |')
    else: print('(không thấy màu có sắc)')
    if r['trung_tinh']:
        print('Màu trung tính (trắng/đen/xám): ' + ', '.join(f'{m["hex"]} ({m["dem"]})' for m in r['trung_tinh']))
    if r['font']: print('Font-family hay dùng: ' + ', '.join(r['font']))
    if r['google_fonts']: print('Font Google Fonts: ' + ', '.join(r['google_fonts']))
    for g in r['ghi_chu']: print('Lưu ý: ' + g)


def main():
    ap = argparse.ArgumentParser(description='Lấy màu + font từ URL / .svg / .png / .css / .html')
    ap.add_argument('nguon', nargs='+'); ap.add_argument('--json', action='store_true', help='in JSON cho máy đọc')
    a = ap.parse_args()
    kq, loi = [], 0
    for n in a.nguon:
        try: kq.append(phan_tich(n))
        except Loi as e: loi += 1; kq.append({'nguon': n, 'loi': str(e)})
        except Exception as e: loi += 1; kq.append({'nguon': n, 'loi': f'{type(e).__name__}: {e}'})
    if a.json: print(json.dumps(kq, ensure_ascii=False, indent=2))
    else:
        for r in kq:
            if 'loi' in r: print(f'\n== {r["nguon"]}\nLỖI: {r["loi"]}')
            else: in_bang(r)
    sys.exit(1 if loi == len(kq) else 0)


if __name__ == '__main__':
    main()
