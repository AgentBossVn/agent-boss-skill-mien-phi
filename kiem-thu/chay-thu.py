#!/usr/bin/env python3
"""Bộ thử skill anh-quang-cao-san-pham trên Windows + Mac (chạy tay hoặc trên GitHub Actions).

Chạy:  python kiem-thu/chay-thu.py            (Python bất kỳ ≥ 3.9; cần mạng để cài gói)
Thất bại bất kỳ khẳng định nào → in "THẤT BẠI" + thoát mã 1. Không gọi API vẽ thật, không dùng khoá thật, không dùng ảnh thương hiệu thật.

Giai đoạn 1 (Python bất kỳ): biên dịch mọi máy → chạy kiem-cong-cu-ve.py → làm đúng lệnh "Máy nền" nó in (uv → môi trường riêng → gói)
  trong HOME tạm (không đụng ~/.venv-anh-qc thật) → chạy lại, thấy ✅.
Giai đoạn 2 (Python riêng vừa cài, cờ --giai-doan-2): thử từng máy bằng ảnh tự vẽ.
"""
import re, argparse, importlib.util, json, os, py_compile, shutil, subprocess, sys, tempfile, time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
WIN, MAC = sys.platform == 'win32', sys.platform == 'darwin'
GOC = Path(__file__).resolve().parent.parent
SCRIPTS = GOC / 'anh-quang-cao-san-pham' / 'scripts'
TAM = GOC / '.tam'
LOI: list[str] = []


def moi_truong(home: Path, them=None):
    e = {k: v for k, v in os.environ.items() if k not in ('PYTHONUTF8', 'PYTHONIOENCODING', 'ARK_API_KEY', 'GEMINI_API_KEY',
                                                           'GOOGLE_API_KEY', 'CODEX_API_KEY', 'OPENAI_API_KEY', 'AGY', 'CHROME',
                                                           'PSModulePath')}  # máy CI chạy pwsh 7: PSModulePath của nó làm powershell.exe 5.1 không nạp được mô-đun
    e['HOME'] = e['USERPROFILE'] = str(home)  # expanduser: Mac/Linux đọc HOME, Windows đọc USERPROFILE
    e.update(them or {})
    return e


def chay(lenh, env, cwd=None, timeout=900):
    """Chạy, trả (mã thoát, đầu ra gộp). Giải mã utf-8 NGHIÊM: đầu ra qua ống mà vỡ tiếng Việt = lỗi."""
    p = subprocess.run([str(x) for x in lenh], env=env, cwd=cwd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
    try:
        return p.returncode, (p.stdout + p.stderr).decode('utf-8')
    except UnicodeDecodeError as e:
        LOI.append(f'đầu ra {Path(str(lenh[1])).name if len(lenh) > 1 else lenh[0]} không phải utf-8: {e}')
        return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')


def khang_dinh(dk, ten, chi_tiet=''):
    print(('  ✓ ' if dk else '  ✗ ') + ten)
    if not dk:
        LOI.append(ten + (f' — {chi_tiet[-700:]}' if chi_tiet else ''))
        if chi_tiet: print('    ' + chi_tiet[-700:].replace('\n', '\n    '))
    return dk


def tieu_de(s): print(f'\n== {s}')


# ---------------------------------------------------------------- giai đoạn 1
def giai_doan_1():
    shutil.rmtree(TAM, ignore_errors=True); home = TAM / 'home'; home.mkdir(parents=True)
    env = moi_truong(home)
    tieu_de('1. Mọi máy biên dịch được')
    for f in sorted(SCRIPTS.glob('*.py')):
        try: py_compile.compile(str(f), cfile=str(TAM / 'pyc' / (f.name + 'c')), doraise=True); khang_dinh(True, f'biên dịch {f.name}')
        except py_compile.PyCompileError as e: khang_dinh(False, f'biên dịch {f.name}', str(e))

    tieu_de('2. kiem-cong-cu-ve.py (lần 1) + cài như người dùng')
    ma, ra = chay([sys.executable, SCRIPTS / 'kiem-cong-cu-ve.py'], env)
    khang_dinh(ma == 0 and 'Công cụ vẽ trên máy này' in ra, 'kiem-cong-cu-ve.py chạy, in tiếng Việt qua ống', ra)
    hang = [l for l in ra.splitlines() if l.startswith('| ') and not l.startswith('| Công cụ ') and not l.startswith('|---')]
    khang_dinh(len(hang) == 8, f'bảng có Máy nền + 7 dòng công cụ (thấy {len(hang)})', ra)
    if WIN: khang_dinh('export PATH' not in ra and 'brew' not in ra and '$env:' in ra, 'Windows: lệnh in ra là PowerShell (không export PATH, không brew)', ra)
    else: khang_dinh('$env:' not in ra and 'Start-Process' not in ra, 'Mac: lệnh in ra không lẫn PowerShell', ra)
    lenh, dang = [], False  # lệnh "Agent chạy" dưới mục **Máy nền …**
    for dong in ra.splitlines():
        if dong.startswith('**'): dang = dong.startswith('**Máy nền')
        elif dang and dong.startswith('- Agent chạy: `'): lenh.append(dong[len('- Agent chạy: `'):-1])
    print(f'  máy nền cần {len(lenh)} lệnh cài')
    for i, l in enumerate(lenh):
        if re.search(r'\b(brew|winget)\b', l): print(f'  (bỏ qua lệnh cần brew/winget trên máy CI: {l[:60]}…)'); continue
        print(f'  > {l[:150]}')
        if WIN:
            ps1 = TAM / f'lenh-{i}.ps1'; ps1.write_text(l + '\n', encoding='utf-8-sig')
            m, o = chay(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1], env)
        else: m, o = chay(['/bin/bash', '-c', l], env)
        khang_dinh(m == 0, f'lệnh cài #{i + 1} chạy xong', o)
    ma, ra = chay([sys.executable, SCRIPTS / 'kiem-cong-cu-ve.py'], env)
    khang_dinh('| Máy nền' in ra and '✅ sẵn sàng' in next((l for l in ra.splitlines() if l.startswith('| Máy nền')), ''),
               'sau khi cài: dòng Máy nền báo ✅ sẵn sàng', ra)
    if LOI: return ket()
    py = home / '.venv-anh-qc' / ('Scripts/python.exe' if WIN else 'bin/python')
    khang_dinh(py.exists(), f'có Python riêng ở {py}')
    if LOI: return ket()
    tieu_de('3. Thử từng máy bằng Python riêng')
    ma = subprocess.run([str(py), str(Path(__file__).resolve()), '--giai-doan-2'], env=env).returncode
    if ma: LOI.append('giai đoạn 2 thất bại (xem trên)')
    ket()


def ket():
    print('\n' + ('THẤT BẠI:\n - ' + '\n - '.join(LOI) if LOI else 'XANH — mọi khẳng định đạt'))
    sys.exit(1 if LOI else 0)


# ---------------------------------------------------------------- giai đoạn 2
def phong(n):
    from PIL import ImageFont
    for p in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', r'C:\Windows\Fonts\arialbd.ttf', '/Library/Fonts/Arial Unicode.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, n)
    return ImageFont.load_default(size=n)


def ve_nhan(khoi_luong):
    """Nhãn thử tự vẽ (không phải nhãn thật của hãng nào)."""
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (1000, 1300), (246, 238, 214)); d = ImageDraw.Draw(im)
    d.rectangle((30, 30, 970, 1270), outline=(150, 20, 20), width=10)
    for chu, y, co in (('CÀ PHÊ HÒA TAN', 140, 92), ('3in1', 420, 260), (khoi_luong, 860, 260)):
        r = d.textbbox((0, 0), chu, font=phong(co))
        d.text(((1000 - (r[2] - r[0])) // 2 - r[0], y), chu, font=phong(co), fill=(120, 10, 10))
    return im


def canh_ve(nhan):
    """Ảnh 'AI vẽ' = nhãn đặt vào cảnh to hơn."""
    from PIL import Image
    nen = Image.new('RGB', (1500, 1700), (70, 90, 120)); n = nhan.resize((900, 1170))
    nen.paste(n, (300, 260)); return nen


def doc_chu(env, py, ve, them=()):
    return chay([py, SCRIPTS / 'doc-chu-so-sanh.py', '--hang', TAM / 'anh' / 'hang.png', '--ve', ve,
                 '--chu', '336 g', '3in1', 'CÀ PHÊ HÒA TAN', *them], env)


def hang_ket_qua(ra):
    d = ra.splitlines(); i = next((k for k, l in enumerate(d) if l.startswith('chữ quan trọng')), None)
    return d[i + 1:i + 4] if i is not None else []


def thu_doc_chu(env, py, ten_luot):
    tieu_de(f'doc-chu-so-sanh.py — {ten_luot}')
    ma, ra = doc_chu(env, py, TAM / 'anh' / 've-dung.png')
    khang_dinh(ma == 0, 'ảnh vẽ ĐÚNG → mã thoát 0', ra)
    r = hang_ket_qua(ra)
    khang_dinh(len(r) == 3 and r[0].rstrip().endswith('ĐẠT'), '  "336 g" ĐẠT', ra)
    khang_dinh(not any('TRƯỢT' in x for x in r), '  ảnh vẽ đúng: không chữ nào TRƯỢT', ra)
    print('  (thông tin) kết quả 3 chữ:', ' | '.join(' '.join(x.split()) for x in r))
    ma, ra = doc_chu(env, py, TAM / 'anh' / 've-dung.png', ('--vung-ve', '0.15,0.1,0.85,0.9', '--vung-hang', '0,0,1,1'))
    khang_dinh(ma == 0, 'ảnh vẽ ĐÚNG, có --vung-ve/--vung-hang → mã thoát 0', ra)
    for ten in ('ve-sai-1336.png', 've-sai-136.png'):
        ma, ra = doc_chu(env, py, TAM / 'anh' / ten)
        r = hang_ket_qua(ra)
        khang_dinh(ma == 2 and len(r) == 3 and r[0].rstrip().endswith('TRƯỢT'), f'{ten}: mã thoát 2 và dòng "336 g" TRƯỢT', ra)
    return ra


ENV_PS = {k: v for k, v in os.environ.items() if k != 'PSModulePath'}  # xem moi_truong()


def vi_co_san():
    m = subprocess.run(['powershell', '-NoProfile', '-Command', "(Get-WindowsCapability -Online -Name 'Language.OCR~~~vi-VN*').State"],
                       capture_output=True, text=True, env=ENV_PS)
    return 'Installed' in m.stdout


def giai_doan_2():
    from PIL import Image, ImageDraw
    home = Path(os.path.expanduser('~')); env = moi_truong(home)
    py = Path(sys.executable); anh = TAM / 'anh'; anh.mkdir(parents=True, exist_ok=True)
    nhan = ve_nhan('336 g'); nhan.save(anh / 'hang.png')
    canh_ve(nhan).save(anh / 've-dung.png')
    canh_ve(ve_nhan('1336 g')).save(anh / 've-sai-1336.png'); canh_ve(ve_nhan('136 g')).save(anh / 've-sai-136.png')
    (anh / 'loi.txt').write_text('Cảnh bàn gỗ, ánh sáng sớm, chừa chỗ chữ phía trên.', encoding='utf-8')

    # --- máy đọc chữ
    if WIN:
        da_co_vi = vi_co_san()
        ra = thu_doc_chu(env, py, f'Windows, lượt 1 ({"đã có" if da_co_vi else "CHƯA có"} gói tiếng Việt)')
        if not da_co_vi:
            khang_dinh('chưa có gói đọc tiếng Việt: so không dấu' in ra, 'lượt 1 in dòng "chưa có gói đọc tiếng Việt: so không dấu"', ra)
            tieu_de('thêm gói đọc tiếng Việt cho Windows (CI có quyền quản trị)')
            m = subprocess.run(['powershell', '-NoProfile', '-Command', 'Add-WindowsCapability -Online -Name "Language.OCR~~~vi-VN~0.0.1.0"'],
                               capture_output=True, text=True, env=ENV_PS)
            if m.returncode == 0 and vi_co_san():
                ra = thu_doc_chu(env, py, 'Windows, lượt 2 (đã thêm gói tiếng Việt)')
                khang_dinh('chưa có gói đọc tiếng Việt' not in ra, 'lượt 2 KHÔNG còn dòng cảnh báo thiếu gói tiếng Việt', ra)
            else: khang_dinh(False, 'Add-WindowsCapability vi-VN OCR không cài được trên máy CI', (m.stdout + m.stderr))
        else: print('  (máy CI đã có gói tiếng Việt từ đầu: bỏ qua lượt 1 "chưa có gói")')
    else: thu_doc_chu(env, py, 'Mac')

    # --- tách nền (ảnh có thẻ EXIF xoay)
    tieu_de('tach-nen-don-gian.py (EXIF xoay)')
    sp = Image.new('RGB', (1000, 800), (255, 255, 255)); ImageDraw.Draw(sp).rounded_rectangle((300, 250, 700, 450), 30, fill=(200, 30, 40))
    ex = sp.getexif(); ex[0x0112] = 6; sp.save(anh / 'san-pham-exif.jpg', quality=95, exif=ex)
    ma, ra = chay([py, SCRIPTS / 'tach-nen-don-gian.py', anh / 'san-pham-exif.jpg', anh / 'vat.png'], env)
    khang_dinh(ma == 0, 'tách nền chạy', ra)
    if ma == 0:
        v = Image.open(anh / 'vat.png'); w, h = v.size
        khang_dinh(v.mode == 'RGBA' and abs(w - 200) <= 12 and abs(h - 400) <= 12, f'EXIF xoay đúng: vật cao hơn rộng ~200x400 (thấy {w}x{h})')
    # --- nền bằng code
    tieu_de('ve-nen-bang-code.py')
    ma, ra = chay([py, SCRIPTS / 've-nen-bang-code.py', '--mau-chinh', '#d4202a', '--kieu', 'toi', '--vong',
                   '--co', '1080x1350', '1920x1080', '1080x1920', '--ra', anh], env)
    khang_dinh(ma == 0, 'dựng nền chạy', ra)
    for co in ('1080x1350', '1920x1080', '1080x1920'):
        p = anh / f'nen-{co}.png'
        khang_dinh(p.exists() and 'x'.join(map(str, Image.open(p).size)) == co, f'nen-{co}.png đúng cỡ')
    # --- ghép sản phẩm thật
    tieu_de('ghep-san-pham-that.py')
    big = Image.new('RGBA', (600, 1200), (0, 0, 0, 0)); ImageDraw.Draw(big).rounded_rectangle((0, 0, 599, 1199), 40, fill=(200, 30, 40, 255)); big.save(anh / 'vat-lon.png')
    ma, ra = chay([py, SCRIPTS / 'ghep-san-pham-that.py', anh / 'nen-1080x1350.png', anh / 'vat-lon.png', anh / 'ghep-1.png',
                   '--cao', '0.42', '--tam-x', '0.5', '--day-y', '0.82'], env)
    khang_dinh(ma == 0 and Image.open(anh / 'ghep-1.png').size == (1080, 1350) and 'CẢNH BÁO' not in ra, 'ghép vật đủ nét: ảnh 1080x1350, không cảnh báo', ra)
    ma, ra = chay([py, SCRIPTS / 'ghep-san-pham-that.py', anh / 'nen-1080x1350.png', anh / 'vat.png', anh / 'ghep-2.png', '--cao', '0.9'], env)
    khang_dinh(ma == 0 and 'CẢNH BÁO' in ra, 'ghép vật nhỏ với --cao 0.9: có "CẢNH BÁO" (tiếng Việt qua ống không vỡ)', ra)
    # --- đặt chữ
    tieu_de('dat-chu.py (Chrome trên Mac, Edge/Chrome trên Windows)')
    spec = importlib.util.spec_from_file_location('dat_chu', SCRIPTS / 'dat-chu.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    trinh = m.tim_chrome(); print('  trình duyệt:', trinh)
    if WIN: khang_dinh(any(k in trinh.lower() for k in ('msedge', 'chrome')), 'Windows tìm được Edge hoặc Chrome', trinh)
    dc = anh / 'dat-chu'; dc.mkdir(exist_ok=True); shutil.copy(anh / 'nen-1080x1350.png', dc / 'nen.png')
    (dc / 'cau-hinh.json').write_text(json.dumps({'thu': {'nen': 'nen.png', 'W': 1080, 'H': 1350, 'khoi': 'left:58px;top:60px', 'co_chu': 64,
        'mau': '#EB4B28', 'dong': [{'kieu': 'dai-toi', 'chu': 'Cà phê hòa tan', 'co': 0.45}, {'kieu': 'lon', 'chu': 'Thơm từng ngụm'}],
        'web': 'vi-du.vn', 'kieu_chu': 'dam'}}, ensure_ascii=False), encoding='utf-8')
    ma, ra = chay([py, SCRIPTS / 'dat-chu.py', dc / 'cau-hinh.json'], env)
    khang_dinh(ma == 0, 'dat-chu chạy', ra)
    png, jpg = dc / 'ra' / 'thu.png', dc / 'ra' / 'thu.jpg'
    if png.exists() and jpg.exists():
        a, b = Image.open(png).convert('RGB'), Image.open(anh / 'nen-1080x1350.png').convert('RGB')
        from PIL import ImageChops, ImageStat
        khang_dinh(a.size == (1080, 1350), f'ảnh đặt chữ đúng cỡ 1080x1350 (thấy {a.size[0]}x{a.size[1]})')
        khang_dinh(sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) > 1, 'ảnh đặt chữ KHÁC nền (chữ đã lên)')
        khang_dinh(jpg.stat().st_size > 5000, 'có cả JPG')
    else: khang_dinh(False, 'dat-chu ra đủ PNG + JPG', ra)
    # --- so sánh, cắt phóng to
    tieu_de('so-sanh-truoc-sau.py · cat-phong-to.py')
    ma, ra = chay([py, SCRIPTS / 'so-sanh-truoc-sau.py', anh / 'ss.jpg', f'Ảnh hãng={anh / "hang.png"}@0,0,500,500', f'Ảnh vẽ={anh / "ve-dung.png"}'], env)
    khang_dinh(ma == 0 and (anh / 'ss.jpg').exists(), 'so-sanh-truoc-sau ra ảnh ghép', ra)
    ma, ra = chay([py, SCRIPTS / 'cat-phong-to.py', anh / 'ct.jpg', anh / 'hang.png', '100', '100', '300', '250', '4', '10'], env)
    khang_dinh(ma == 0 and Image.open(anh / 'ct.jpg').size == (800, 600), 'cat-phong-to ×4 ra 800x600', ra)

    # --- máy vẽ với máy chủ giả (không tiền, không khoá thật)
    tieu_de('ve-anh-byteplus.py (máy chủ giả)')
    gia = TAM / 'gia'; gia.mkdir(exist_ok=True)
    (gia / 'sitecustomize.py').write_text('''import base64, io
import requests
from PIL import Image
class _Tra:
    ok = True; status_code = 200; text = ''
    def json(self):
        b = io.BytesIO(); Image.new('RGB', (64, 80), (10, 120, 200)).save(b, 'PNG')
        return {'data': [{'b64_json': base64.b64encode(b.getvalue()).decode()}]}
requests.post = lambda *a, **k: _Tra()
''', encoding='utf-8')
    kd = home / '.config' / 'anh-qc'; kd.mkdir(parents=True, exist_ok=True)
    (kd / 'byteplus.key').write_text('KHOA-GIA-' + 'x' * 24 + '\n', encoding='utf-8')
    e_gia = moi_truong(home, {'PYTHONPATH': str(gia)})
    ma, ra = chay([py, SCRIPTS / 've-anh-byteplus.py', '--loi-nho', anh / 'loi.txt', '--mau', anh / 'hang.png', '--ti-le', '4:5', '--ra', anh / 've' / 'bp.jpg'], e_gia)
    khang_dinh(ma == 0 and 'OK' in ra and (anh / 've' / 'bp.jpg').exists(), 'byteplus: ảnh giả về, lưu đúng tên .jpg, mã 0', ra)
    so = anh / 've' / 'so-chi.jsonl'
    khang_dinh(so.exists() and json.loads(so.read_text(encoding='utf-8').splitlines()[-1]).get('ok') is True, 'byteplus: sổ so-chi.jsonl ghi ok=true')
    ma, ra = chay([py, SCRIPTS / 've-anh-byteplus.py', '--loi-nho', anh / 'loi.txt', '--ti-le', '4:5', '--tran-usd', '0.01', '--ra', anh / 've' / 'bp2.jpg'], e_gia)
    khang_dinh(ma != 0 and 'trần' in ra, 'byteplus: vượt trần tiền → từ chối', ra)

    tieu_de('ve-anh-goi-google.py (agy giả báo hết lượt)')
    agy = gia / ('agy.cmd' if WIN else 'agy')
    j = '{"status":"ERROR","error":"RESOURCE_EXHAUSTED: quota reached"}'
    if WIN: agy.write_text(f'@echo off\r\necho {j}\r\nexit /b 0\r\n', encoding='ascii')
    else: agy.write_text(f"#!/bin/sh\necho '{j}'\n", encoding='utf-8'); agy.chmod(0o755)
    t0 = time.time()
    ma, ra = chay([py, SCRIPTS / 've-anh-goi-google.py', '--loi-nho', anh / 'loi.txt', '--mau', anh / 'hang.png', '--ti-le', '4:5', '--ra', anh / 've' / 'g.png'],
                  moi_truong(home, {'AGY': str(agy)}))
    khang_dinh(ma == 1 and 'hết lượt' in ra and time.time() - t0 < 60, 'google: agy giả hết lượt → dừng ngay, mã 1, báo "hết lượt"', ra)

    tieu_de('ve-anh-goi-chatgpt.py (codex giả đăng nhập bằng khoá API → từ chối, tìm codex qua PATH)')
    cd = gia / 'codex-bin'; cd.mkdir(exist_ok=True)
    if WIN: (cd / 'codex.cmd').write_text('@echo off\r\necho Logged in using an API key\r\n', encoding='ascii')
    else: (cd / 'codex').write_text('#!/bin/sh\necho "Logged in using an API key"\n', encoding='utf-8'); (cd / 'codex').chmod(0o755)
    e = moi_truong(home); e['PATH'] = str(cd) + os.pathsep + e['PATH']
    ma, ra = chay([py, SCRIPTS / 've-anh-goi-chatgpt.py', '--loi-nho', anh / 'loi.txt', '--ra', anh / 've' / 'c.png'], e)
    khang_dinh(ma != 0 and 'LỖI Codex không đăng nhập' in ra, 'chatgpt: tìm được codex giả, từ chối vì khoá API (không tốn tiền)', ra)

    tieu_de('In tiếng Việt khi đầu ra qua ống')
    for ten in ('cat-phong-to.py', 'dat-chu.py', 'so-sanh-truoc-sau.py'):
        ma, ra = chay([py, SCRIPTS / ten], env)
        khang_dinh(ma != 0 and 'Cách chạy' in ra and 'UnicodeEncodeError' not in ra, f'{ten} không tham số: in "Cách chạy…" đủ dấu, không UnicodeEncodeError', ra)
    sys.exit(1 if LOI else 0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--giai-doan-2', action='store_true'); a = ap.parse_args()
    if a.giai_doan_2: giai_doan_2()
    else: giai_doan_1()
