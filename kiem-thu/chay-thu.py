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
GIT_BASH = next((p for p in (r'C:\Program Files\Git\bin\bash.exe', r'C:\Program Files (x86)\Git\bin\bash.exe') if os.path.exists(p)), None)


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
    khang_dinh('$env:' not in ra and 'export PATH' not in ra and 'Start-Process' not in ra and 'brew' not in ra and '\\scripts\\' not in ra and 'scripts\\' not in ra,
               'lệnh in ra không riêng của shell nào (không $env:, export PATH, Start-Process, brew, dấu \\ trong đường dẫn)', ra)
    if WIN: khang_dinh('py -3 "' in ra or 'python "' in ra, 'Windows: lệnh gọi máy kiểm qua py -3 (không dính "python" giả của Store)', ra)
    cam = re.findall(r'\|\s*(?:sh|bash|iex)\b|curl -|@latest|brew install|Notepad', ra)
    khang_dinh(not cam, f'không dòng lệnh nào tải-rồi-chạy-ngay / @latest / brew install / Notepad (thấy: {cam})', ra)
    khoa_txt = (SCRIPTS / 'khoa-thu-vien.txt').read_text(encoding='utf-8')
    khang_dinh('--require-hashes' in (SCRIPTS / 'kiem-cong-cu-ve.py').read_text(encoding='utf-8') and khoa_txt.count('--hash=sha256:') > 100
               and 'winrt-windows-media-ocr==4!10.0.28000.2957 ; sys_platform == \'win32\'' in khoa_txt, 'cài thư viện dùng --require-hashes + tệp khoá có mã băm (gói Mac + Windows đủ)')
    khang_dinh('--cai nen' in ra, 'máy nền cài qua lệnh con --cai nen (không cần shell riêng)', ra)
    khang_dinh(not re.findall(r'@openai/codex(?!@\d)|wrangler(?!@\d)(?= (?:dev|login))', ra), 'Codex và wrangler (nếu in ra) đều có bản ghim', ra)

    tieu_de('2a. --cai uv: tải THẬT 1 bản uv ghim, đối chiếu SHA-256 thật (HOME riêng)')
    home_uv = TAM / 'home-uv'; home_uv.mkdir()
    env_uv = moi_truong(home_uv)
    ma, ra_uv = chay([sys.executable, SCRIPTS / 'kiem-cong-cu-ve.py', '--cai', 'uv'], env_uv)
    khang_dinh(ma == 0 and 'Đã khớp SHA-256' in ra_uv, '--cai uv chạy xong, báo đã khớp SHA-256', ra_uv)
    uv_moi = home_uv / '.local' / 'bin' / ('uv.exe' if WIN else 'uv')
    khang_dinh(uv_moi.exists(), f'uv nằm ở {uv_moi}')
    if uv_moi.exists():
        ma, ra_ver = chay([uv_moi, '--version'], env_uv)
        khang_dinh(ma == 0 and '0.13.8' in ra_ver, 'uv vừa cài chạy được, đúng bản 0.13.8', ra_ver)
    (TAM / 'gia').mkdir(exist_ok=True)
    gia_sai = TAM / 'gia' / 'cai-uv-sai-ma.py'
    gia_sai.write_text('''import io, runpy, sys, urllib.request
class _R(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False
urllib.request.urlopen = lambda *a, **k: _R(b'khong-phai-uv')
sys.argv = [sys.argv[1], '--cai', 'uv']
runpy.run_path(sys.argv[0], run_name='__main__')
''', encoding='utf-8')
    ma, ra_sai = chay([sys.executable, gia_sai, SCRIPTS / 'kiem-cong-cu-ve.py'], moi_truong(TAM / 'home-uv-sai'))
    khang_dinh(ma != 0 and 'SHA-256 không khớp' in ra_sai and not (TAM / 'home-uv-sai' / '.local').exists(),
               'tải về sai nội dung → báo "SHA-256 không khớp", KHÔNG cài gì', ra_sai)
    lenh, dang = [], False  # lệnh "Agent chạy" dưới mục **Máy nền …**
    for dong in ra.splitlines():
        if dong.startswith('**'): dang = dong.startswith('**Máy nền')
        elif dang and dong.startswith('- Agent chạy: `'): lenh.append(dong[len('- Agent chạy: `'):-1])
    print(f'  máy nền cần {len(lenh)} lệnh cài')
    for i, l in enumerate(lenh):
        if re.search(r'\b(brew|winget)\b', l): print(f'  (bỏ qua lệnh cần brew/winget trên máy CI: {l[:60]}…)'); continue
        print(f'  > {l[:150]}')
        if WIN:  # mọi dòng in ra phải chạy được ở CẢ PowerShell lẫn Git Bash; thêm exit $LASTEXITCODE vì PowerShell không tự trả mã lỗi của lệnh ngoài
            m, o = chay(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', l + '; exit $LASTEXITCODE'], env)
            khang_dinh(m == 0, f'lệnh #{i + 1} chạy xong qua PowerShell (mã thoát thật)', o)
            if GIT_BASH:
                m, o = chay([GIT_BASH, '-c', l], env)
                khang_dinh(m == 0, f'lệnh #{i + 1} chạy xong qua Git Bash (dòng in ra dùng được ở shell của Claude Code trên Windows)', o)
            else: khang_dinh(False, 'máy CI Windows phải có Git Bash')
            continue
        m, o = chay(['/bin/bash', '-c', l], env)
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


def ve_nhan(khoi_luong, ten='CÀ PHÊ HÒA TAN'):
    """Nhãn thử tự vẽ (không phải nhãn thật của hãng nào)."""
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (1000, 1300), (246, 238, 214)); d = ImageDraw.Draw(im)
    d.rectangle((30, 30, 970, 1270), outline=(150, 20, 20), width=10)
    for chu, y, co in ((ten, 140, 92), ('3in1', 420, 260), (khoi_luong, 860, 260)):
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
    if MAC:
        khang_dinh(len(r) == 3 and r[2].rstrip().endswith('ĐẠT'), '  "CÀ PHÊ HÒA TAN" ĐẠT', ra)
        khang_dinh(len(r) == 3 and (r[1].rstrip().endswith('ĐẠT') or 'MÁY KHÔNG ĐỌC ĐƯỢC' in r[1]), '  "3in1" ĐẠT hoặc MÁY KHÔNG ĐỌC ĐƯỢC', ra)
        ma_d, ra_d = doc_chu(env, py, TAM / 'anh' / 've-sai-dau.png')
        r_d = hang_ket_qua(ra_d)
        khang_dinh(ma_d == 2 and len(r_d) == 3 and r_d[2].rstrip().endswith('TRƯỢT'), '  ve-sai-dau.png ("CA PHE HOA TAN" mất dấu): Mac phải TRƯỢT, mã 2', ra_d)
    else:
        khang_dinh('Bộ đọc chữ:' in ra, '  Windows in dòng "Bộ đọc chữ: <ngôn ngữ>" (có ít nhất 1 ngôn ngữ đọc được)', ra)
        khang_dinh(len(r) == 3 and all(x.rstrip().endswith('ĐẠT') or 'CẦN SOÁT MẮT' in x for x in r), '  Windows: mỗi chữ ĐẠT hoặc CẦN SOÁT MẮT (không TRƯỢT giả)', ra)
    print('  (thông tin) kết quả 3 chữ:', ' | '.join(' '.join(x.split()) for x in r))
    ma, ra = doc_chu(env, py, TAM / 'anh' / 've-dung.png', ('--vung-ve', '0.15,0.1,0.85,0.9', '--vung-hang', '0,0,1,1'))
    khang_dinh(ma == 0, 'ảnh vẽ ĐÚNG, có --vung-ve/--vung-hang → mã thoát 0', ra)
    for ten in ('ve-sai-1336.png', 've-sai-136.png'):
        ma, ra = doc_chu(env, py, TAM / 'anh' / ten)
        r = hang_ket_qua(ra)
        khang_dinh(ma == 2 and len(r) == 3 and r[0].rstrip().endswith('TRƯỢT'), f'{ten}: mã thoát 2 và dòng "336 g" TRƯỢT', ra)
    return ra


def thu_keyring(env, py, gia, ve_bp, e_gia, anh):
    """Khoá GIẢ vào kho khoá hệ điều hành, máy vẽ + máy kiểm đọc ra. Chỉ chạy trên máy CI (biến CI): máy người thật không bị ghi gì."""
    tieu_de('keyring: khoá giả trong kho khoá hệ điều hành (Credential Manager / Keychain)')
    if not os.environ.get('CI'): print('  (bỏ qua: không phải máy CI, không ghi vào kho khoá thật của máy này)'); return
    tep = gia / 'thu-keyring.py'
    tep.write_text('''import sys, keyring
if sys.argv[1] == 'ghi': keyring.set_password('anh-qc', 'byteplus', 'KHOA-GIA-' + 'k' * 24)
elif sys.argv[1] == 'xoa': keyring.delete_password('anh-qc', 'byteplus')
else: sys.exit(0 if (keyring.get_password('anh-qc', 'byteplus') or '') == sys.argv[2] else 1)
''', encoding='utf-8')
    try: ma, ra = chay([py, tep, 'ghi'], env, timeout=60)
    except subprocess.TimeoutExpired: ma, ra = -9, 'treo quá 60 giây (Keychain chờ mở khoá / hộp xin quyền, máy CI không có người bấm)'
    if ma != 0 and MAC:
        print('  (bỏ qua keyring trên Mac CI: Keychain không ghi được trên máy CI — ' + (ra.strip().splitlines() or ['?'])[-1][:150] + ')'); return
    if not khang_dinh(ma == 0, 'ghi khoá giả vào kho khoá (keyring.set_password)', ra): return
    try:
        ma, ra = chay(ve_bp + ['--ra', anh / 've' / 'kr.jpg'], e_gia)
        khang_dinh(ma == 0 and 'OK' in ra and (anh / 've' / 'kr.jpg').exists(), 'byteplus: KHÔNG có biến, KHÔNG có tệp khoá — đọc được khoá từ keyring, ảnh giả về', ra)
        ma, ra = chay([sys.executable, SCRIPTS / 'kiem-cong-cu-ve.py'], env)
        d4 = next((l for l in ra.splitlines() if l.startswith('| 4.')), '')
        khang_dinh('✅ đã có khoá' in d4, 'kiem-cong-cu-ve: dòng 4 (Seedream) báo ✅ đã có khoá nhờ keyring', ra)
        khang_dinh('KHOA-GIA' not in ra, 'kiem-cong-cu-ve KHÔNG in khoá ra', ra)
        if WIN:  # hộp nhập kín của Windows: dựng form thật (không bấm được trên CI), đường ống PowerShell → Python → kho khoá chạy thật
            e = dict(env, ANHQC_CHI_TAO='1')
            ma, ra = chay([py, SCRIPTS / 'kiem-cong-cu-ve.py', '--nhap-khoa', 'byteplus'], e)
            khang_dinh(ma == 0 and 'Đã lưu khoá byteplus' in ra and 'TAO-OK' not in ra, '--nhap-khoa (Windows): form dựng được, khoá đi qua ống vào kho khoá, KHÔNG in ra', ra)
            ma, ra = chay([py, tep, 'doc', 'TAO-OK'], env)
            khang_dinh(ma == 0, '--nhap-khoa (Windows): giá trị qua ống đúng là cái đã đưa vào kho khoá', ra)
    finally:
        chay([py, tep, 'xoa'], env)


def giai_doan_2():
    from PIL import Image, ImageDraw
    home = Path(os.path.expanduser('~')); env = moi_truong(home)
    py = Path(sys.executable); anh = TAM / 'anh'; anh.mkdir(parents=True, exist_ok=True)
    nhan = ve_nhan('336 g'); nhan.save(anh / 'hang.png')
    canh_ve(nhan).save(anh / 've-dung.png')
    canh_ve(ve_nhan('1336 g')).save(anh / 've-sai-1336.png'); canh_ve(ve_nhan('136 g')).save(anh / 've-sai-136.png')
    canh_ve(ve_nhan('336 g', 'CA PHE HOA TAN')).save(anh / 've-sai-dau.png')
    (anh / 'loi.txt').write_text('Cảnh bàn gỗ, ánh sáng sớm, chừa chỗ chữ phía trên.', encoding='utf-8')

    # --- máy đọc chữ
    if WIN: thu_doc_chu(env, py, 'Windows (không có bộ đọc tiếng Việt: so không dấu)')
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
    if WIN:  # đường Edge chưa từng thử vì máy CI có Chrome: ép dùng Edge qua biến CHROME
        edge = next((x for x in (r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe') if os.path.exists(x)), '')
        if khang_dinh(bool(edge), 'máy CI Windows có Edge'):
            dc2 = anh / 'dat-chu-edge'; dc2.mkdir(exist_ok=True); shutil.copy(dc / 'nen.png', dc2 / 'nen.png'); shutil.copy(dc / 'cau-hinh.json', dc2 / 'cau-hinh.json')
            ma, ra = chay([py, SCRIPTS / 'dat-chu.py', dc2 / 'cau-hinh.json'], moi_truong(home, {'CHROME': edge}))
            ok = ma == 0 and (dc2 / 'ra' / 'thu.png').exists()
            khang_dinh(ok and Image.open(dc2 / 'ra' / 'thu.png').size == (1080, 1350), 'dat-chu bằng EDGE (CHROME=msedge.exe): ảnh 1080x1350', ra)
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
    e_gia = moi_truong(home, {'PYTHONPATH': str(gia)})
    ve_bp = [py, SCRIPTS / 've-anh-byteplus.py', '--loi-nho', anh / 'loi.txt', '--mau', anh / 'hang.png', '--ti-le', '4:5']
    thu_keyring(env, py, gia, ve_bp, e_gia, anh)
    (kd / 'byteplus.key').write_text('KHOA-GIA-' + 'x' * 24 + '\n', encoding='utf-8')  # tệp cũ (chỉ đọc) vẫn dùng được
    ma, ra = chay(ve_bp + ['--ra', anh / 've' / 'bp.jpg'], e_gia)
    khang_dinh(ma == 0 and 'OK' in ra and (anh / 've' / 'bp.jpg').exists(), 'byteplus: khoá ở tệp cũ → ảnh giả về, lưu đúng tên .jpg, mã 0', ra)
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
