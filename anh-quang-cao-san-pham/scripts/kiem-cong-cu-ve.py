# Kiểm trên máy người dùng: đã có / đã nối những công cụ vẽ nào, mỗi công cụ tốn tiền gì, chọn rồi thì Agent làm gì.
# Agent chạy máy này ở Bước 0, đưa bảng cho người dùng chọn. Chọn xong mà chưa sẵn sàng → Agent cho người dùng xem danh sách
# sẽ cài (tên + nguồn chính thức + bản ghim), HỎI ĐỒNG Ý, rồi mới chạy các dòng "Agent chạy"; người dùng làm dòng "Bạn làm".
# Cài xong chạy lại máy này, thấy ✅ mới vẽ. Máy CHỈ ĐỌC (trừ --cai, --chay, --mo, --nhap-khoa), KHÔNG in khoá / token ra.
# MỌI dòng "Agent chạy" chạy được ở CẢ HAI shell (bash / Git Bash và PowerShell): đường dẫn dùng "/", việc cài do CHÍNH Python làm qua
# lệnh con (subprocess với danh sách đối số, không cần shell, tự thêm các thư mục công cụ vào PATH) — không tiền tố $env:Path, không "scripts\".
# Không có dòng cài nào kiểu "tải về rồi chạy ngay"; mọi thứ ghim đúng bản: uv (SHA-256 viết cứng), thư viện Python
# (mã băm ở scripts/khoa-thu-vien*.txt), Codex + wrangler (npm, bản ghim).
# Chạy:  python3 kiem-cong-cu-ve.py                 → bảng công cụ (Windows: py -3 thay python3)
#        ... --cai uv       → tải ĐÚNG 1 bản uv từ GitHub releases của astral-sh, đối chiếu SHA-256 viết cứng, khớp mới giải nén vào ~/.local/bin
#        ... --cai nen      → uv (nếu chưa có) + Python 3.12 riêng ~/.venv-anh-qc + thư viện khoá mã băm (khoa-thu-vien.txt)
#        ... --cai gemini   → thư viện Gemini trả tiền (khoa-thu-vien-gemini.txt)   ... --cai codex → npm i -g @openai/codex@<bản ghim>
#        ... --cai node | chrome  → Windows: winget (bản hãng). Mac: người dùng tự tải ở trang chính thức (lệnh --mo mở trang)
#        ... --chay codex-login | codex-logout | agy | cloudflare-login   → chạy công cụ đó (tự tìm đường), đầu ra hiện thẳng
#        ... --mo <địa chỉ web>  → mở trình duyệt
#        ... --nhap-khoa [gemini|byteplus] → hộp nhập KÍN (Mac: hộp của macOS · Windows: hộp của Windows), khoá đi qua ống nội bộ vào kho khoá
#          của hệ điều hành (Mac = Keychain, Windows = Credential Manager, gói keyring), service "anh-qc". KHÔNG in, KHÔNG ghi tệp.
#          Máy tự chuyển sang Python riêng (có gói keyring) nếu đang chạy bằng Python khác.
# Windows (16/11/2026): môi trường Python riêng ở %USERPROFILE%\.venv-anh-qc\Scripts\python.exe, cài bằng uv; Windows mới tinh chưa có Python
#   thì Agent làm bước mồi trong SKILL.md (winget Python.Python.3.12). Máy đọc chữ = Windows.Media.Ocr qua PyWinRT. Mac: Chrome / Node tải ở trang chính thức.
# Bản 3 (15/11/2026): Tầng 1 gói AI bạn ĐANG TRẢ (ChatGPT, Gemini, Claude) → Tầng 2 máy vẽ các hãng qua API
#   (miễn phí trước, rồi trả tiền) → Tầng 3 công cụ làm ảnh chuyên nghiệp bạn đã dùng sẵn.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import hashlib, io, os, platform, shutil, socket, subprocess, sys, tarfile, urllib.request, webbrowser, zipfile

NHA = os.path.expanduser('~')
WIN = sys.platform == 'win32'
APPDATA, LOCALAPPDATA = os.environ.get('APPDATA', ''), os.environ.get('LOCALAPPDATA', '')
KHOA = {'gemini': ('Gemini API (bắt đầu bằng AIza…)', os.path.join(NHA, '.config', 'anh-qc', 'gemini.key')),  # tệp = chỗ lưu CỦA BẢN CŨ, chỉ đọc
        'byteplus': ('BytePlus ModelArk (trang API Key)', os.path.join(NHA, '.config', 'anh-qc', 'byteplus.key'))}
KHOA_GEMINI, KHOA_BYTEPLUS = KHOA['gemini'][1], KHOA['byteplus'][1]
DICH_VU_KHOA = 'anh-qc'  # service trong kho khoá hệ điều hành; username = gemini | byteplus
GOC = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(NHA, '.venv-anh-qc', 'Scripts', 'python.exe') if WIN else os.path.join(NHA, '.venv-anh-qc', 'bin', 'python')  # môi trường riêng của skill (dòng "Cài 1 lần" trong SKILL.md)
SCRIPT = os.path.abspath(__file__)
SLASH = lambda p: p.replace('\\', '/')  # đường dẫn in ra dùng "/" cho cả bash lẫn PowerShell
PYTHON_KHOI = ('py -3' if shutil.which('py') else 'python') if WIN else 'python3'  # Windows: "py -3" không dính lệnh "python" giả của Microsoft Store
KIEM = f'{PYTHON_KHOI} "{SLASH(SCRIPT)}"'  # đường tuyệt đối: Agent có thể đang đứng ở thư mục khác; chỉ dấu " bao đường dẫn (bash + PowerShell đều hiểu)
CODEX_BAN, WRANGLER_BAN = '0.169.0', '4.162.0'  # ghim (npm view, 16/11/2026); Codex bản này có công cụ vẽ ảnh (image_generation)
THU_MUC_CONG_CU = ([os.path.join(NHA, '.local', 'bin'), os.path.join(LOCALAPPDATA, 'Programs', 'OpenAI', 'Codex', 'bin'), os.path.join(LOCALAPPDATA, 'agy', 'bin'),
                    os.path.join(APPDATA, 'npm'), os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs')] if WIN
                   else ['/opt/homebrew/bin', '/usr/local/bin', os.path.join(NHA, '.local', 'bin')])
ENV_CAI = dict(os.environ, PATH=os.pathsep.join(THU_MUC_CONG_CU + [os.environ.get('PATH', '')]))  # phiên Agent không tự có đường tới công cụ vừa cài


def chay(lenh, cho=20, env=None):
    try:
        p = subprocess.run(lenh, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=cho, stdin=subprocess.DEVNULL, env=env)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except (OSError, subprocess.TimeoutExpired):
        return -1, ''


def tim(ten, *them):
    return shutil.which(ten) or next((p for p in them if os.path.exists(p)), None)


def tim_trinh_duyet():  # Chrome trước, không có thì Edge (cùng nền Chromium, cùng cờ headless) — khớp dat-chu.py
    if os.environ.get('CHROME'): return os.environ['CHROME']
    pf = [os.environ.get(k, '') for k in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA')]
    cho = (['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
           + [os.path.join(d, r) for d in pf if d for r in (r'Google\Chrome\Application\chrome.exe', r'Microsoft\Edge\Application\msedge.exe')])
    return next((p for p in cho if os.path.exists(p)), None) \
        or next((shutil.which(n) for n in ('google-chrome', 'chromium', 'chromium-browser', 'chrome', 'msedge', 'microsoft-edge') if shutil.which(n)), None)


UV_BAN = '0.13.8'  # ghim; mã băm lấy từ tệp .sha256 của đúng bản release này (github.com/astral-sh/uv/releases/tag/0.13.8)
UV_GOI = {('darwin', 'arm64'): ('uv-aarch64-apple-darwin.tar.gz', '6b71028a6b904f2ae3340ef52e595512de807d06c0a20eaef2f692581b246558'),
          ('darwin', 'x64'): ('uv-x86_64-apple-darwin.tar.gz', 'a04c2ffeac28b2003a2c13caf538ab425fcd7def3e4a41571f4a8fb370a66af3'),
          ('win32', 'x64'): ('uv-x86_64-pc-windows-msvc.zip', '529e78a9cec6cd7e3e014f7ecd8bda0c113969d4ed0f2efeedb85c30943325b8'),
          ('win32', 'arm64'): ('uv-aarch64-pc-windows-msvc.zip', '59e6d919bed1f72035e622a7c930058f08a8931c4c78ceaf9f56e7fb74dd2c48')}
# Hộp nhập kín của Windows (Windows Forms, ô gõ hiện dấu chấm): chữ gõ vào in ra stdout; nhãn qua biến ANHQC_NHAN
HOP_KIN_WIN = ("Add-Type -AssemblyName System.Windows.Forms; "
               "$f=New-Object Windows.Forms.Form; $f.Text='Anh quang cao'; $f.ClientSize='420,130'; $f.StartPosition='CenterScreen'; $f.TopMost=$true; "
               "$l=New-Object Windows.Forms.Label; $l.Text=$env:ANHQC_NHAN; $l.SetBounds(12,10,396,40); "
               "$t=New-Object Windows.Forms.TextBox; $t.UseSystemPasswordChar=$true; $t.SetBounds(12,55,396,24); "
               "$b=New-Object Windows.Forms.Button; $b.Text='OK'; $b.SetBounds(328,90,80,28); $b.DialogResult='OK'; "
               "$f.AcceptButton=$b; $f.Controls.AddRange(@($l,$t,$b)); "
               "if($env:ANHQC_CHI_TAO){[Console]::Out.Write('TAO-OK'); exit}; "
               "if($f.ShowDialog() -eq 'OK'){[Console]::Out.Write($t.Text)}")


def co_khoa_keyring(ten):  # hỏi Python riêng: kho khoá hệ điều hành có khoá `ten` chưa (chỉ trả có/không, không in khoá)
    if not os.path.exists(PY): return False
    ma, _ = chay([PY, '-c', 'import keyring, sys; k = keyring.get_password(sys.argv[1], sys.argv[2]); sys.exit(0 if k and len(k) >= 20 else 1)',
                  DICH_VU_KHOA, ten], cho=30)
    return ma == 0


def cai_uv():
    may = platform.machine().lower()
    kieu = (sys.platform if sys.platform in ('darwin', 'win32') else '', 'arm64' if may in ('arm64', 'aarch64') else 'x64' if may in ('x86_64', 'amd64') else '')
    if kieu not in UV_GOI: sys.exit(f'LỖI chưa có bản uv ghim cho máy này ({sys.platform}, {may}).')
    ten_goi, ma_chuan = UV_GOI[kieu]
    url = f'https://github.com/astral-sh/uv/releases/download/{UV_BAN}/{ten_goi}'
    print(f'Tải uv {UV_BAN} từ {url}')
    try:
        with urllib.request.urlopen(url, timeout=120) as r: du_lieu = r.read()
    except OSError as e: sys.exit(f'LỖI không tải được uv: {e}')
    ma_that = hashlib.sha256(du_lieu).hexdigest()
    if ma_that != ma_chuan: sys.exit(f'LỖI mã SHA-256 không khớp (chuẩn {ma_chuan}, tải về {ma_that}). KHÔNG cài. Báo người dùng.')
    dich = os.path.join(NHA, '.local', 'bin'); os.makedirs(dich, exist_ok=True)
    can = {'uv.exe', 'uvx.exe'} if WIN else {'uv', 'uvx'}
    if ten_goi.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(du_lieu)) as z: tep = {os.path.basename(n): z.read(n) for n in z.namelist() if os.path.basename(n) in can}
    else:
        with tarfile.open(fileobj=io.BytesIO(du_lieu), mode='r:gz') as t:
            tep = {os.path.basename(m.name): t.extractfile(m).read() for m in t.getmembers() if m.isfile() and os.path.basename(m.name) in can}
    if not tep: sys.exit('LỖI gói uv không có tệp uv.')
    for ten, nd in tep.items():
        d = os.path.join(dich, ten); tam = d + '.moi'
        with open(tam, 'wb') as f: f.write(nd)
        os.chmod(tam, 0o755); os.replace(tam, d)
    print(f'Đã khớp SHA-256 và cài uv {UV_BAN} vào {dich} ({", ".join(sorted(tep))}).')


def chay_that(lenh):  # chạy công cụ, đầu ra hiện thẳng; tự tìm đường (kể cả .cmd trên Windows); trả mã thoát
    exe = shutil.which(lenh[0], path=ENV_CAI['PATH'])
    if not exe: sys.exit(f'LỖI không thấy lệnh {lenh[0]} trên máy (cài trước đã).')
    print('> ' + ' '.join([lenh[0]] + [SLASH(x) if os.sep in x else x for x in lenh[1:]]), flush=True)
    try: return subprocess.call([exe] + lenh[1:], env=ENV_CAI)
    except OSError as e: sys.exit(f'LỖI không chạy được {lenh[0]}: {e}')


def tep_khoa_thu_vien(ten): return os.path.join(GOC, ten)


def cai(viec):
    if viec == 'uv': return cai_uv()
    if viec in ('nen', 'gemini'):
        if not shutil.which('uv', path=ENV_CAI['PATH']): cai_uv()
        if viec == 'nen' and not os.path.exists(PY):
            if chay_that(['uv', 'venv', '--python', '3.12', os.path.dirname(os.path.dirname(PY))]): sys.exit('LỖI uv không tạo được môi trường Python 3.12.')
        ma = chay_that(['uv', 'pip', 'install', '--python', PY, '--require-hashes', '-r', tep_khoa_thu_vien('khoa-thu-vien.txt' if viec == 'nen' else 'khoa-thu-vien-gemini.txt')])
        if ma: sys.exit(f'LỖI cài thư viện thất bại (mã {ma}).')
        return
    if viec == 'codex':
        ma = chay_that(['npm', 'i', '-g'] + ([] if WIN else ['--prefix', os.path.join(NHA, '.local')]) + [f'@openai/codex@{CODEX_BAN}'])
        if ma: sys.exit(f'LỖI cài Codex thất bại (mã {ma}). Chưa có Node thì cài Node trước.')
        return
    if viec in ('node', 'chrome') and WIN:
        ma = chay_that(['winget', 'install', '--id', 'OpenJS.NodeJS.LTS' if viec == 'node' else 'Google.Chrome', '-e',
                        '--accept-package-agreements', '--accept-source-agreements'])
        if ma: sys.exit(f'LỖI winget thất bại (mã {ma}). Nếu hiện hộp xin quyền (UAC) thì bấm Yes rồi chạy lại.')
        return
    sys.exit(f'LỖI không có việc cài "{viec}" trên máy này (Mac: Node / Chrome người dùng tự tải ở trang chính thức).')


def chay_viec(viec):
    cac = {'codex-login': ['codex', 'login'], 'codex-logout': ['codex', 'logout'], 'agy': ['agy'],
           'cloudflare-login': ['npx', '--yes', f'wrangler@{WRANGLER_BAN}', 'login']}
    if viec not in cac: sys.exit('LỖI --chay nhận: ' + ' | '.join(cac))
    return chay_that(cac[viec])


def doi(tham_so):
    i = sys.argv.index(tham_so)
    if i + 1 >= len(sys.argv): sys.exit(f'LỖI {tham_so} cần thêm 1 giá trị.')
    return sys.argv[i + 1]


if '--cai' in sys.argv: cai(doi('--cai')); sys.exit(0)
if '--chay' in sys.argv: sys.exit(chay_viec(doi('--chay')))
if '--mo' in sys.argv:
    url = doi('--mo')
    if not url.startswith('https://'): sys.exit('LỖI chỉ mở địa chỉ https://')
    print('Mở trình duyệt:', url, '→ mở được' if webbrowser.open(url) else '→ KHÔNG mở được, người dùng tự mở địa chỉ này'); sys.exit(0)

if '--nhap-khoa' in sys.argv:
    loai = next((a for a in sys.argv if a in KHOA), 'gemini'); nhan = KHOA[loai][0]
    try: import keyring
    except ImportError:  # Python hệ thống không có keyring ⇒ chạy lại chính máy này bằng Python riêng
        if os.path.exists(PY) and os.path.abspath(sys.executable) != os.path.abspath(PY): sys.exit(subprocess.call([PY, SCRIPT] + sys.argv[1:]))
        sys.exit('LỖI chưa có Python riêng của skill (thiếu gói keyring): chạy --cai nen trước.')
    if WIN:
        e = dict(os.environ, ANHQC_NHAN=f'Dán khoá {nhan} rồi bấm OK. Khoá chỉ lưu trong Credential Manager của máy này.')
        ma, ra = chay(['powershell.exe', '-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass', '-Command', HOP_KIN_WIN], cho=600, env=e)
    elif sys.platform == 'darwin':
        ma, ra = chay(['osascript', '-e', 'activate', '-e', f'text returned of (display dialog "Dán khoá {nhan} rồi bấm OK. '
                       'Khoá chỉ lưu trong Keychain của máy này." default answer "" with hidden answer with title "Ảnh quảng cáo")'], cho=600)
    else: sys.exit('Hộp nhập kín chỉ có trên Mac và Windows.')
    khoa = ra.strip() if ma == 0 else ''
    if not khoa or ' ' in khoa: sys.exit('Chưa lưu: ô trống hoặc người dùng bấm Huỷ.')
    try: keyring.set_password(DICH_VU_KHOA, loai, khoa)
    except Exception as e: sys.exit(f'LỖI không ghi được vào kho khoá hệ điều hành: {type(e).__name__}')
    print(f'Đã lưu khoá {loai} vào kho khoá của máy (service {DICH_VU_KHOA}); không in ra, không ghi tệp.'); sys.exit(0)

mac = sys.platform == 'darwin'
node = tim('npm', '/opt/homebrew/bin/npm', '/usr/local/bin/npm', os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'))
if node: CAI_NODE, BAN_NODE = [], []
elif WIN: CAI_NODE, BAN_NODE = [KIEM + ' --cai node'], ['nếu hiện hộp xin quyền (UAC) thì bấm Yes']
else: CAI_NODE, BAN_NODE = [KIEM + ' --mo https://nodejs.org/en/download'], ['tải bản LTS cho Mac (.pkg), mở tệp, bấm Continue/Install theo hướng dẫn (có thể hỏi mật khẩu máy), xong báo Agent']
bang = []  # (tên, tiền, trạng thái, lệnh Agent chạy, việc bạn làm)

# --- Máy nền: mọi đường đều cần (soát, dán nhãn, đặt chữ)
lenh, ban = [], []
THU_VIEN = 'import PIL, numpy, scipy, requests, keyring' + (', Vision' if sys.platform == 'darwin' else ', winrt.windows.media.ocr' if WIN else '')
if not (os.path.exists(PY) and chay([PY, '-c', THU_VIEN])[0] == 0):
    # python3 sẵn của Apple là 3.9 ⇒ không cài nổi bản thư viện đã ghim (cần ≥ 3.12) ⇒ uv tự tải Python 3.12 riêng
    lenh.append(KIEM + ' --cai nen')  # uv (nếu chưa có) + Python 3.12 riêng + thư viện khoá mã băm
if not tim_trinh_duyet():  # Chrome hoặc Edge đều được (Windows luôn có Edge)
    if WIN:
        lenh += [KIEM + ' --cai chrome']; ban += ['nếu hiện hộp xin quyền (UAC) thì bấm Yes']
    else:
        lenh += [KIEM + ' --mo https://www.google.com/chrome/']; ban += ['tải Chrome (hoặc Edge) cho Mac, mở tệp tải về, kéo vào thư mục Applications, xong báo Agent']
bang.append(('Máy nền (đường nào cũng cần: soát, đọc chữ, dán nhãn, đặt chữ)', '0đ', '⚠️ thiếu' if lenh else '✅ sẵn sàng', lenh, ban))
nen_ok = not lenh

# ===== TẦNG 1 — gói AI bạn ĐANG TRẢ: Agent của gói đó tự vẽ, 0đ thêm
# --- 1. Gói ChatGPT qua Codex
CAI_CODEX = KIEM + ' --cai codex'  # Mac: vào ~/.local/bin, khỏi cần quyền quản trị
codex = tim('codex', os.path.join(NHA, '.local', 'bin', 'codex'), '/opt/homebrew/bin/codex', '/usr/local/bin/codex', os.path.join(APPDATA, 'npm', 'codex.cmd'))
lenh, ban, tt = list(CAI_NODE), list(BAN_NODE), '✅ đã nối'
if not codex: lenh.append(CAI_CODEX); tt = '⚠️ chưa cài'
dang_nhap = chay([codex, 'login', 'status'])[1] if codex else ''
if 'ChatGPT' not in dang_nhap:
    if 'API key' in dang_nhap: tt = '⚠️ đang đăng nhập bằng KHOÁ API (vẽ sẽ TÍNH TIỀN OpenAI)'; lenh.append(KIEM + ' --chay codex-logout')
    elif codex: tt = '⚠️ chưa đăng nhập'
    lenh.append(KIEM + ' --chay codex-login')
    ban.append('trên trình duyệt chọn "Sign in with ChatGPT", đăng nhập tài khoản có gói Plus/Pro')
elif not any(l.split()[:1] == ['image_generation'] and l.split()[-1:] == ['true'] for l in chay([codex, 'features', 'list'])[1].splitlines()):
    tt = '⚠️ Codex chưa bật công cụ vẽ'; lenh += CAI_NODE + [CAI_CODEX]
bang.append(('1. Gói ChatGPT — Codex tự vẽ (ảnh đẹp nhất đã đo)', '0đ thêm, trừ hạn mức gói ChatGPT Plus/Pro (~35 nghìn token gói/ảnh)', tt, lenh, ban))

# --- 2. Gói Google AI Pro/Ultra qua Antigravity CLI (công cụ generate_image có sẵn)
agy = tim('agy', os.path.join(NHA, '.local', 'bin', 'agy'), os.path.join(LOCALAPPDATA, 'agy', 'bin', 'agy.exe'))
ma_agy, ra_agy = chay([agy, 'models'], cho=40) if agy else (-1, '')
if not agy: tt, lenh, ban = '⚠️ chưa cài', [KIEM + ' --mo https://antigravity.google/download'], [
    'tải + cài Antigravity, đăng nhập tài khoản Google có gói AI Pro/Ultra, bật công cụ dòng lệnh `agy` theo hướng dẫn trong ứng dụng']
elif ma_agy != 0 or 'gemini' not in ra_agy: tt, lenh, ban = '⚠️ chưa đăng nhập', [KIEM + ' --chay agy'], ['đăng nhập tài khoản Google có gói AI Pro/Ultra trong cửa sổ agy']
else: tt, lenh, ban = '✅ đã nối', [], []
bang.append(('2. Gói Gemini (Google AI Pro) — Antigravity tự vẽ', '0đ thêm, trừ hạn mức vẽ ảnh của gói (trần TUẦN riêng)', tt, lenh, ban))

# --- 3. Claude tự dựng bằng code: ảnh thật của hãng cắt nền + nền vẽ bằng code + chữ HTML (không AI vẽ)
tach = 'Vision của Mac' if mac and not WIN and chay(['xcode-select', '-p'])[0] == 0 else 'máy tách nền đơn giản (ảnh hãng phải nền trắng/trơn)'
bang.append(('3. Claude tự dựng bằng code (đúng 100% sản phẩm, nhưng chỉ là ảnh đồ hoạ như banner, KHÔNG đẹp bằng ảnh AI vẽ)', '0đ',
             ('✅ sẵn sàng · tách nền bằng ' + tach) if nen_ok else '⚠️ cài máy nền trước', [], []))

# ===== TẦNG 2 — máy vẽ các hãng qua API: miễn phí trước, trả tiền sau (CHỈ khi bạn tự chọn)
# --- 4. Seedream 4.5 qua BytePlus ModelArk (ByteDance): 200 ảnh miễn phí
co_bp = bool(os.environ.get('ARK_API_KEY')) or co_khoa_keyring('byteplus') or (os.path.exists(KHOA_BYTEPLUS) and os.path.getsize(KHOA_BYTEPLUS) > 20) \
    or (mac and chay(['security', 'find-generic-password', '-s', 'byteplus-ark-claude-thu-anh'])[0] == 0)
bang.append(('4. Seedream 4.5 (BytePlus, hãng ByteDance) — ảnh thứ 2 sau ChatGPT', '200 ảnh miễn phí; sau đó ~0,04 USD/ảnh. Cần thẻ Visa/Master hoặc PayPal để KÍCH HOẠT (chưa trừ tiền)',
             '✅ đã có khoá' if co_bp else '⚠️ chưa có khoá',
             [] if co_bp else [KIEM + ' --mo https://console.byteplus.com/ark/region:ap-southeast-1/openManagement', KIEM + ' --nhap-khoa byteplus'],
             [] if co_bp else ['đăng ký BytePlus, BẬT "Free Credits Only Mode" (chỉ dùng phần miễn phí), thêm thẻ/PayPal, bấm Activate dòng Seedream 4.5',
                               'trang API Key → Create → dán khoá vào hộp nhập kín hiện lên (khoá vào kho khoá của máy; KHÔNG dán vào chat)']))

# --- 5. Cloudflare Workers AI, phần miễn phí hằng ngày
cf = [os.path.join(NHA, 'Library', 'Preferences', '.wrangler', 'config', 'default.toml'),
      os.path.join(APPDATA, 'xdg.config', '.wrangler', 'config', 'default.toml'),
      os.path.join(os.environ.get('XDG_CONFIG_HOME') or os.path.join(NHA, '.config'), '.wrangler', 'config', 'default.toml')]
da_cf = any(os.path.exists(f) and 'oauth_token' in open(f, encoding='utf-8', errors='ignore').read() for f in cf) \
    or bool(os.environ.get('CLOUDFLARE_API_TOKEN') and os.environ.get('CLOUDFLARE_ACCOUNT_ID'))
with socket.socket() as s: s.settimeout(1); cong_bat = s.connect_ex(('127.0.0.1', 8841)) == 0
bang.append(('5. Cloudflare — miễn phí, ảnh kém nhất', '0đ trong ~40 ảnh/ngày; quá mức máy tự dừng, không tính tiền',
             ('✅ đã nối · ' + ('cổng vẽ đang bật' if cong_bat else 'Agent bật cổng khi vẽ')) if da_cf and node else '⚠️ chưa nối',
             CAI_NODE + ([] if da_cf else [KIEM + ' --chay cloudflare-login']),
             BAN_NODE + ([] if da_cf else ['đăng nhập Cloudflare trên trình duyệt (chưa có thì đăng ký miễn phí), bấm "Allow"'])))

# --- 6. Trả tiền Gemini (Nano Banana 2.1)
co_khoa = bool(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')) or co_khoa_keyring('gemini') \
    or (os.path.exists(KHOA_GEMINI) and os.path.getsize(KHOA_GEMINI) > 20)
co_genai = os.path.exists(PY) and chay([PY, '-c', 'import google.genai'])[0] == 0
bang.append(('6. Gemini API trả tiền (Nano Banana 2.1)', '~0,05 USD/ảnh 2K (~0,25 USD/sản phẩm), trừ thẻ gắn với khoá Google — CHỈ khi bạn tự chọn',
             '✅ đã có khoá' if co_khoa and co_genai else '⚠️ chưa có khoá' if not co_khoa else '⚠️ thiếu thư viện',
             ([] if co_genai else [KIEM + ' --cai gemini'])
             + ([] if co_khoa else [KIEM + ' --mo https://aistudio.google.com/apikey', KIEM + ' --nhap-khoa gemini']),
             [] if co_khoa else ['tạo khoá + gắn thẻ thanh toán trên trang Google', 'dán khoá vào hộp nhập kín hiện lên (khoá vào kho khoá của máy; KHÔNG dán vào chat)']))


# ===== TẦNG 3 — công cụ làm ảnh chuyên nghiệp
bang.append(('7. Công cụ chuyên nghiệp bạn ĐÃ dùng (Photoroom, Pebblely, Canva…)', 'theo gói bạn đang trả',
             '— nói tên công cụ, Agent dùng tài khoản/khoá của bạn', [], []))

print('# Công cụ vẽ trên máy này — xếp theo thứ tự nên dùng\n(Tầng 1: gói AI bạn đang trả · Tầng 2: máy vẽ qua API · Tầng 3: công cụ chuyên nghiệp)\n'
      '(mọi đường: phần Agent chạy trừ hạn mức gói Agent của bạn, ~120 nghìn token/sản phẩm)\n'
      f'Python riêng của skill (mọi lệnh `python` trong SKILL.md = đường này): {SLASH(PY)}\n'
      'Mọi dòng "Agent chạy" bên dưới chạy được ở cả bash (Git Bash) lẫn PowerShell.\n')
print('**Nói trước về độ đẹp:** muốn ảnh đẹp như ảnh chụp → gói ChatGPT (1), gói Gemini (2) hoặc đường trả tiền (4 sau 200 ảnh, 6). '
      'Đường 0đ (3, 5) ra ảnh kém hẳn, chỉ dùng tạm. Ảnh ví dụ từng đường: https://github.com/AgentBossVn/agent-boss-skills/tree/main/vi-du\n')
print('| Công cụ | Tiền | Trên máy bạn |\n|---|---|---|')
for ten, tien, tt, _, _ in bang: print(f'| {ten} | {tien} | {tt} |')
chua = [b for b in bang if b[2].startswith('⚠️') and (b[3] or b[4])]
if chua:
    print('\n## Chọn rồi mà chưa sẵn sàng: Agent cho người dùng xem danh sách sẽ cài, HỎI ĐỒNG Ý, rồi mới chạy; bạn làm phần của bạn')
    for ten, _, _, lenh, ban in chua:
        print(f'\n**{ten}**')
        for l in lenh:
            print(f'- Agent chạy: `{l}`')
        for l in ban: print(f'- Bạn làm: {l}')
