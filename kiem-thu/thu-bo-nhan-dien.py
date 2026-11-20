#!/usr/bin/env python3
"""Bộ thử skill bo-nhan-dien-thuong-hieu (chạy tay hoặc trên GitHub Actions, Mac + Windows).

Chạy:  python kiem-thu/thu-bo-nhan-dien.py      (Python ≥ 3.9, chỉ thư viện chuẩn, không cần mạng)
Sai khẳng định nào → in "THẤT BẠI" + thoát mã 1. HOME tạm (không đụng ~/.agent-boss thật).
Phần chụp ảnh cần Chrome/Edge/Brave/Chromium; không có → in "BỎ QUA".
"""
import json, os, shutil, struct, subprocess, sys, tempfile, zlib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
GOC = Path(__file__).resolve().parent.parent
SC = GOC / 'bo-nhan-dien-thuong-hieu' / 'scripts'
LOI = []


def khang_dinh(dk, ten, chi_tiet=''):
    print(('  ✓ ' if dk else '  ✗ ') + ten)
    if not dk:
        LOI.append(ten);
        if chi_tiet: print('    ' + str(chi_tiet)[-700:].replace('\n', '\n    '))
    return dk


def chay(lenh, env, timeout=300):
    p = subprocess.run([sys.executable, '-X', 'utf8'] + [str(x) for x in lenh], env=env, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')


def png(path: Path, w, h, rgba_fn):
    """Tự vẽ PNG RGBA 8-bit không xen kẽ."""
    raw = b''.join(b'\x00' + b''.join(bytes(rgba_fn(x, y)) for x in range(w)) for y in range(h))
    def chunk(k, d): return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def dung_bo_thu(thu: Path, co_hinh: bool) -> Path:
    bo = thu / ('bo-co-hinh' if co_hinh else 'bo-khong-hinh'); (bo / 'logo').mkdir(parents=True)
    png(bo / 'logo' / 'logo-tren-nen.png', 120, 30, lambda x, y: (255, 255, 255, 255) if 5 < y < 25 else (0, 0, 0, 0))
    png(bo / 'logo' / 'logo-tren-nen-sang.png', 120, 30, lambda x, y: (0, 74, 239, 255) if 5 < y < 25 else (0, 0, 0, 0))
    tk = {'ten': 'Tiệm Nhà Mây', 'phien_ban': '1.0', 'ngay': '2026-11-20', 'cau_dinh_vi': 'Bánh ngọt làm mỗi sáng', 'web': 'nhamay.vn',
          'mau': {'nen': '#004AEF', 'chu_tren_nen': '#FFFFFF', 'chu_phu_tren_nen': '#DCE6FE', 'nhan': '#07EF9C', 'chu_tren_nhan': '#062A1C',
                  'the': '#0034B8', 'nen_sang': '#FFFFFF', 'muc': '#1F2430', 'muc_phu': '#4A5468'},
          'font': {'ten': 'Be Vietnam Pro', 'google_fonts': True, 'dam_tieu_de': 700}, 'bo_goc': {'nut': '6px', 'the': '12px'},
          'logo': {'tren_nen': 'logo/logo-tren-nen.png', 'tren_nen_sang': 'logo/logo-tren-nen-sang.png', 'vuong': None},
          'hinh_dac_trung': None}
    if co_hinh:
        png(bo / 'logo' / 'hinh-dac-trung.png', 40, 40, lambda x, y: (7, 239, 156, 255))
        tk['hinh_dac_trung'] = {'tep': 'logo/hinh-dac-trung.png', 'mo_ta': 'hình thử'}
    (bo / 'tokens.json').write_text(json.dumps(tk, ensure_ascii=False, indent=2), encoding='utf-8')
    return bo


def main():
    thu = Path(tempfile.mkdtemp(prefix='thu-bnd-')); home = thu / 'home'; home.mkdir()
    env = {k: v for k, v in os.environ.items() if k != 'CHROME'}
    env['HOME'] = env['USERPROFILE'] = str(home)
    try:
        print('\n== 1. lay-mau.py')
        xanh = thu / 'xanh.png'; png(xanh, 60, 60, lambda x, y: (0, 74, 239, 255) if y < 50 else (0, 0, 0, 0))
        ma, ra = chay([SC / 'lay-mau.py', xanh, '--json'], env)
        try: kq = json.loads(ra)[0]; mau = kq['mau'][0]['hex']
        except Exception: kq, mau = {}, ''
        khang_dinh(ma == 0 and mau == '#004AEF', f'PNG: màu chủ đạo đọc đúng #004AEF (thấy {mau!r})', ra)
        svg = thu / 'logo.svg'; svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#07EF9C"/><circle fill="#07EF9C"/><path fill="#FFF"/></svg>', encoding='utf-8')
        ma, ra = chay([SC / 'lay-mau.py', svg, '--json'], env)
        try: mau = json.loads(ra)[0]['mau'][0]['hex']
        except Exception: mau = ''
        khang_dinh(ma == 0 and mau == '#07EF9C', f'SVG: màu chủ đạo đọc đúng #07EF9C (thấy {mau!r}), #FFF xếp vào trung tính', ra)
        ma, ra = chay([SC / 'lay-mau.py', thu / 'anh.jpg'], env)
        khang_dinh(ma == 1 and 'LỖI' in ra, 'tệp không có/JPG: báo lỗi tiếng Việt, thoát 1', ra)

        html = thu / 'trang.html'
        html.write_text('<html><body><p>' + 'Tom &#039;n&#039; Jerry &#038; &#160; ' * 50 + '<a href="#fab">x</a><a href="#003399">y</a></p>'
                        '<style>:root{--brand:#123456}</style></body></html>', encoding='utf-8')
        ma, ra = chay([SC / 'lay-mau.py', html, '--json'], env)
        try: mau = json.loads(ra)[0]['mau'][0]['hex']; ds = [m['hex'] for m in json.loads(ra)[0]['mau']]
        except Exception: mau, ds = '', []
        khang_dinh(ma == 0 and mau == '#123456' and len(ds) == 1, f'HTML: chỉ quét vùng CSS — entity/anchor không thành màu (thấy {ds})', ra)
        css = thu / 'a.css'; css.write_text('a{color:#abc} b{color:rgb(200,10,30)}', encoding='utf-8')
        ma, ra = chay([SC / 'lay-mau.py', css, '--json'], env)
        khang_dinh(ma == 0 and len(json.loads(ra)[0]['mau']) == 2, 'CSS: quét toàn tệp (hex 3 chữ số + rgb())', ra)
        lon = thu / 'lon.png'; png(lon, 2200, 2200, lambda x, y: (0, 74, 239, 255))
        ma, ra = chay([SC / 'lay-mau.py', lon, '--json'], env)
        try: mau = json.loads(ra)[0]['mau'][0]['hex']
        except Exception: mau = ''
        khang_dinh(ma == 0 and mau == '#004AEF', 'PNG lớn (4,8 triệu điểm) vẫn đọc, lấy mẫu thưa', ra)

        print('\n== 2. do-tuong-phan.py')
        ma, ra = chay([SC / 'do-tuong-phan.py', '#000000', '#FFFFFF', '--json'], env)
        try: t = json.loads(ra)['ti_le']
        except Exception: t = None
        khang_dinh(ma == 0 and t == 21, f'đen/trắng = 21 (thấy {t})', ra)
        bo = dung_bo_thu(thu, True)
        ma, ra = chay([SC / 'do-tuong-phan.py', bo], env)
        khang_dinh(ma == 0 and 'CẤM dùng làm chữ' in ra, 'bộ tốt: thoát 0, bảng có phán tiếng Việt', ra)
        kem = thu / 'bo-kem'; (kem).mkdir(); tk = json.loads((bo / 'tokens.json').read_text(encoding='utf-8')); tk['mau']['chu_tren_nen'] = '#8899AA'
        (kem / 'tokens.json').write_text(json.dumps(tk), encoding='utf-8')
        ma, ra = chay([SC / 'do-tuong-phan.py', kem], env)
        khang_dinh(ma == 1, 'bộ có cặp bắt buộc kém: thoát 1', ra)
        tk['mau']['chu_tren_nen'] = '#FFFFFF'; tk['mau']['muc_phu'] = '#EEEEEE'
        (kem / 'tokens.json').write_text(json.dumps(tk), encoding='utf-8')
        ma, ra = chay([SC / 'do-tuong-phan.py', kem], env)
        khang_dinh(ma == 1, 'chữ phụ nền sáng không đọc được (#EEE trên trắng): thoát 1', ra)

        print('\n== 3. dung-bo.py')
        ho_so = home / '.agent-boss' / 'thuong-hieu.json'; ho_so.parent.mkdir()
        ho_so.write_text(json.dumps({'ten': 'cũ', 'cau_ket': 'Theo dõi để xem thêm', 'nhac': None}, ensure_ascii=False), encoding='utf-8')
        ma, ra = chay([SC / 'dung-bo.py', bo], env)
        khang_dinh(ma == 0, 'dung-bo bộ có hình đặc trưng chạy xong', ra)
        ten_mau = ['bai-dang-4x5', 'story-9x16', 'banner-ngang', 'slide-bia', 'slide-noi-dung', 'tai-lieu-a4', 'chu-ky-email']
        khang_dinh(all((bo / 'mau' / f'{n}.html').is_file() for n in ten_mau) and (bo / 'guideline.html').is_file(), 'đủ 7 mẫu + guideline.html')
        tat_ca = [(bo / 'mau' / f'{n}.html').read_text(encoding='utf-8') for n in ten_mau] + [(bo / 'guideline.html').read_text(encoding='utf-8')]
        khang_dinh(not any('{{' in s for s in tat_ca), 'không còn "{{" sót')
        khang_dinh('../logo/logo-tren-nen.png' in tat_ca[0] and 'hinh-dac-trung.png' in tat_ca[0] and '--nen:#004AEF' in tat_ca[0], 'mẫu có đường dẫn logo ../logo/, hình đặc trưng, biến màu')
        hs = json.loads(ho_so.read_text(encoding='utf-8'))
        khang_dinh(hs.get('ten') == 'Tiệm Nhà Mây' and hs.get('mau_nhan') == '#07EF9C' and hs.get('cau_ket') == 'Theo dõi để xem thêm'
                   and hs.get('bo_nhan_dien') == str(bo.resolve()) and Path(hs.get('logo', '')).is_absolute(), 'hồ sơ chung ghi đúng + giữ khoá cau_ket cũ', hs)
        bo2 = dung_bo_thu(thu, False)
        ma, ra = chay([SC / 'dung-bo.py', bo2, '--khong-ho-so'], env)
        s2 = [(bo2 / 'mau' / f'{n}.html').read_text(encoding='utf-8') for n in ten_mau] if ma == 0 else ['{{']
        khang_dinh(ma == 0 and not any('HINH' in s or 'class="glow"' in s or '{{' in s for s in s2), 'bộ không hình đặc trưng: mẫu bỏ hết khối HINH + quầng sáng', ra)
        khang_dinh(json.loads(ho_so.read_text(encoding='utf-8'))['ten'] == 'Tiệm Nhà Mây', '--khong-ho-so: hồ sơ không bị ghi đè')
        sua = bo / 'mau' / 'slide-bia.html'; sua.write_text(sua.read_text(encoding='utf-8') + '<!--SUA-TAY-->', encoding='utf-8')
        ma, ra = chay([SC / 'dung-bo.py', bo, '--chi-guideline', '--khong-ho-so'], env)
        khang_dinh(ma == 0 and '<!--SUA-TAY-->' in sua.read_text(encoding='utf-8'), '--chi-guideline: giữ bản mẫu đã sửa tay', ra)
        ho_so.write_bytes(b'\xef\xbb\xbf' + json.dumps({'khoa_video': 'giu'}).encode())
        ma, ra = chay([SC / 'dung-bo.py', bo, '--chi-guideline'], env)
        hs = json.loads(ho_so.read_text(encoding='utf-8-sig'))
        khang_dinh(ma == 0 and hs.get('khoa_video') == 'giu' and hs.get('ten') == 'Tiệm Nhà Mây', 'hồ sơ có BOM (Windows): đọc được, giữ khoá cũ', ra)
        ho_so.write_text('{hỏng', encoding='utf-8')
        ma, ra = chay([SC / 'dung-bo.py', bo, '--chi-guideline'], env)
        khang_dinh(ma == 1 and ho_so.read_text(encoding='utf-8') == '{hỏng', 'hồ sơ hỏng: dừng, KHÔNG ghi đè', ra)
        hong = thu / 'bo-hong'; hong.mkdir(); tk = json.loads((bo / 'tokens.json').read_text(encoding='utf-8')); tk['mau']['nhan'] = 'xanh'; del tk['mau']['muc']
        (hong / 'tokens.json').write_text(json.dumps(tk), encoding='utf-8')
        ma, ra = chay([SC / 'dung-bo.py', hong, '--khong-ho-so'], env)
        khang_dinh(ma == 1 and 'mau.muc' in ra and 'mau.nhan' in ra, 'tokens.json sai: báo rõ chỗ sai, thoát 1', ra)

        print('\n== 4. chup-anh.py')
        sys.path.insert(0, str(SC)); import importlib.util
        spec = importlib.util.spec_from_file_location('chup_anh', SC / 'chup-anh.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        if not m.tim_trinh_duyet(): print('  BỎ QUA: máy này không có Chrome/Edge/Brave/Chromium')
        else:
            ma, ra = chay([SC / 'chup-anh.py', bo / 'mau'], env)
            khang_dinh(ma == 0, 'chụp cả thư mục mau/', ra)
            for n, (w, h) in zip(ten_mau, [(1080, 1350), (1080, 1920), (1200, 630), (1920, 1080), (1920, 1080), (794, 1123), (600, 200)]):
                f = bo / 'mau' / 'xem-truoc' / f'{n}.png'
                kt = struct.unpack('>II', f.read_bytes()[16:24]) if f.is_file() else None
                khang_dinh(kt == (w, h), f'{n}.png đúng khổ {w}×{h} (thấy {kt})')
            ma, ra = chay([SC / 'chup-anh.py', bo / 'mau' / 'story-9x16.html', '--ra', thu / 'le'], env)
            khang_dinh(ma == 0 and (thu / 'le' / 'story-9x16.png').is_file(), 'chụp 1 tệp lẻ với --ra', ra)
    finally:
        shutil.rmtree(thu, ignore_errors=True)
    if LOI:
        print(f'\nTHẤT BẠI: {len(LOI)} khẳng định sai'); sys.exit(1)
    print('\nXANH: mọi khẳng định đạt')


if __name__ == '__main__':
    main()
