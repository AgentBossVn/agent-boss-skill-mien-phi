# Kiểm trên máy người dùng: đã có / đã nối những công cụ vẽ nào, mỗi công cụ tốn tiền gì, chọn rồi thì Agent làm gì.
# Agent chạy máy này ở Bước 0, đưa bảng cho người dùng chọn. Chọn xong mà chưa sẵn sàng → Agent cho người dùng xem danh sách
# sẽ cài (tên + nguồn chính thức + bản ghim), HỎI ĐỒNG Ý, rồi mới chạy các dòng "Agent chạy"; người dùng làm dòng "Bạn làm".
# Cài xong chạy lại máy này, thấy ✅ mới vẽ. Máy CHỈ ĐỌC (trừ --nhap-khoa, --cai-uv), KHÔNG in khoá / token ra.
# Không có dòng cài nào kiểu "tải về rồi chạy ngay"; mọi thứ ghim đúng bản: uv (SHA-256 viết cứng), thư viện Python
# (mã băm ở scripts/khoa-thu-vien*.txt), Codex + wrangler (npm, bản ghim).
# Chạy:  python3 kiem-cong-cu-ve.py              → bảng công cụ
#        python3 kiem-cong-cu-ve.py --cai-uv     → tải ĐÚNG 1 bản uv từ GitHub releases của astral-sh, đối chiếu SHA-256 viết cứng,
#          khớp mới giải nén uv/uvx vào ~/.local/bin (Windows %USERPROFILE%\.local\bin). Chỉ dùng thư viện chuẩn Python.
#        <Python riêng> kiem-cong-cu-ve.py --nhap-khoa [gemini|byteplus] → hộp nhập KÍN (Mac: hộp của macOS · Windows: hộp của Windows),
#          khoá đi qua ống nội bộ vào kho khoá của hệ điều hành (Mac = Keychain, Windows = Credential Manager, gói keyring),
#          service "anh-qc". KHÔNG in, KHÔNG ghi tệp. Phải chạy bằng Python riêng (có gói keyring).
# Windows (16/11/2026): máy in lệnh PowerShell, môi trường Python riêng ở %USERPROFILE%\.venv-anh-qc\Scripts\python.exe, cài bằng uv;
#   máy đọc chữ = Windows.Media.Ocr qua gói PyWinRT. Mac: Chrome / Node tải ở trang chính thức (người dùng bấm), không Homebrew.
# Bản 3 (15/11/2026): Tầng 1 gói AI bạn ĐANG TRẢ (ChatGPT, Gemini, Claude) → Tầng 2 máy vẽ các hãng qua API
#   (miễn phí trước, rồi trả tiền) → Tầng 3 công cụ làm ảnh chuyên nghiệp bạn đã dùng sẵn.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import hashlib, io, os, platform, shutil, socket, subprocess, sys, tarfile, urllib.request, zipfile

NHA = os.path.expanduser('~')
WIN = sys.platform == 'win32'
APPDATA, LOCALAPPDATA = os.environ.get('APPDATA', ''), os.environ.get('LOCALAPPDATA', '')
KHOA = {'gemini': ('Gemini API (bắt đầu bằng AIza…)', os.path.join(NHA, '.config', 'anh-qc', 'gemini.key')),  # tệp = chỗ lưu CỦA BẢN CŨ, chỉ đọc
        'byteplus': ('BytePlus ModelArk (trang API Key)', os.path.join(NHA, '.config', 'anh-qc', 'byteplus.key'))}
KHOA_GEMINI, KHOA_BYTEPLUS = KHOA['gemini'][1], KHOA['byteplus'][1]
DICH_VU_KHOA = 'anh-qc'  # service trong kho khoá hệ điều hành; username = gemini | byteplus
GOC = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(NHA, '.venv-anh-qc', 'Scripts', 'python.exe') if WIN else os.path.join(NHA, '.venv-anh-qc', 'bin', 'python')  # môi trường riêng của skill (dòng "Cài 1 lần" trong SKILL.md)
# Phiên Agent không tự có đường tới công cụ vừa cài ⇒ mọi lệnh in ra đều kèm tiền tố này
TIEN_TO = ('$env:Path = "$env:USERPROFILE\\.local\\bin;$env:LOCALAPPDATA\\Programs\\OpenAI\\Codex\\bin;$env:LOCALAPPDATA\\agy\\bin;$env:APPDATA\\npm;$env:ProgramFiles\\nodejs;" + $env:Path; '
           if WIN else 'export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"; ')
PYTHON_KHOI = 'python' if WIN else 'python3'  # lệnh chạy chính máy này (Windows: python, không có python3)
KIEM = f'{PYTHON_KHOI} "{os.path.abspath(__file__)}"'  # đường tuyệt đối: Agent có thể đang đứng ở thư mục khác
KIEM_RIENG = ('& ' if WIN else '') + f'"{PY}" "{os.path.abspath(__file__)}"'  # chạy bằng Python riêng (cần gói keyring)
TU_MAY = set()  # lệnh gọi lại chính máy này — in ra KHÔNG kèm tiền tố PATH
NPM, NPX = ('npm.cmd', 'npx.cmd') if WIN else ('npm', 'npx')  # PowerShell chặn npm.ps1 khi chính sách mặc định ⇒ gọi .cmd
CODEX_BAN, WRANGLER_BAN = '0.169.0', '4.162.0'  # ghim (npm view, 16/11/2026); Codex bản này có công cụ vẽ ảnh (image_generation)
# Thư viện cài bằng uv + mã băm: scripts/khoa-thu-vien.txt (nguồn thu-vien.in), riêng Gemini trả tiền: khoa-thu-vien-gemini.txt
CAI_PIP = f'uv pip install --python "{PY}" --require-hashes -r '
MO_TRANG = 'Start-Process ' if WIN else 'open '


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


if '--cai-uv' in sys.argv:
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
    print(f'Đã khớp SHA-256 và cài uv {UV_BAN} vào {dich} ({", ".join(sorted(tep))}).'); sys.exit(0)

if '--nhap-khoa' in sys.argv:
    loai = next((a for a in sys.argv if a in KHOA), 'gemini'); nhan = KHOA[loai][0]
    try: import keyring
    except ImportError: sys.exit('LỖI chạy bằng Python riêng của skill (có gói keyring), không phải Python hệ thống: ' + PY)
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
uv = tim('uv', os.path.join(NHA, '.local', 'bin', 'uv.exe' if WIN else 'uv'))
CAI_UV_TRUOC = [] if uv else [KIEM + ' --cai-uv']
TU_MAY.update(CAI_UV_TRUOC)
node = tim('npm', '/opt/homebrew/bin/npm', '/usr/local/bin/npm', os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'))
if node: CAI_NODE, BAN_NODE = [], []
elif WIN: CAI_NODE, BAN_NODE = ['winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements'], ['nếu hiện hộp xin quyền (UAC) thì bấm Yes']
else: CAI_NODE, BAN_NODE = [MO_TRANG + 'https://nodejs.org/en/download'], ['tải bản LTS cho Mac (.pkg), mở tệp, bấm Continue/Install theo hướng dẫn (có thể hỏi mật khẩu máy), xong báo Agent']
bang = []  # (tên, tiền, trạng thái, lệnh Agent chạy, việc bạn làm)

# --- Máy nền: mọi đường đều cần (soát, dán nhãn, đặt chữ)
lenh, ban = [], []
THU_VIEN = 'import PIL, numpy, scipy, requests, keyring' + (', Vision' if sys.platform == 'darwin' else ', winrt.windows.media.ocr' if WIN else '')
if not (os.path.exists(PY) and chay([PY, '-c', THU_VIEN])[0] == 0):
    # python3 sẵn của Apple là 3.9 ⇒ không cài nổi bản thư viện đã ghim (cần ≥ 3.12) ⇒ uv tự tải Python 3.12 riêng
    lenh += CAI_UV_TRUOC + ([f'uv venv --python 3.12 "{os.path.join(NHA, ".venv-anh-qc")}"'] if not os.path.exists(PY) else [])
    lenh.append(CAI_PIP + f'"{os.path.join(GOC, "khoa-thu-vien.txt")}"')
if not tim_trinh_duyet():  # Chrome hoặc Edge đều được (Windows luôn có Edge)
    if WIN:
        lenh += ['winget install --id Google.Chrome -e --accept-package-agreements --accept-source-agreements']; ban += ['nếu hiện hộp xin quyền (UAC) thì bấm Yes']
    else:
        lenh += [MO_TRANG + 'https://www.google.com/chrome/']; ban += ['tải Chrome (hoặc Edge) cho Mac, mở tệp tải về, kéo vào thư mục Applications, xong báo Agent']
bang.append(('Máy nền (đường nào cũng cần: soát, đọc chữ, dán nhãn, đặt chữ)', '0đ', '⚠️ thiếu' if lenh else '✅ sẵn sàng', lenh, ban))
nen_ok = not lenh

# ===== TẦNG 1 — gói AI bạn ĐANG TRẢ: Agent của gói đó tự vẽ, 0đ thêm
# --- 1. Gói ChatGPT qua Codex
CAI_CODEX = f'{NPM} i -g ' + ('' if WIN else '--prefix "$HOME/.local" ') + f'@openai/codex@{CODEX_BAN}'  # Mac: vào ~/.local/bin, khỏi cần quyền quản trị
codex = tim('codex', os.path.join(NHA, '.local', 'bin', 'codex'), '/opt/homebrew/bin/codex', '/usr/local/bin/codex', os.path.join(APPDATA, 'npm', 'codex.cmd'))
lenh, ban, tt = list(CAI_NODE), list(BAN_NODE), '✅ đã nối'
if not codex: lenh.append(CAI_CODEX); tt = '⚠️ chưa cài'
dang_nhap = chay([codex, 'login', 'status'])[1] if codex else ''
if 'ChatGPT' not in dang_nhap:
    if 'API key' in dang_nhap: tt = '⚠️ đang đăng nhập bằng KHOÁ API (vẽ sẽ TÍNH TIỀN OpenAI)'; lenh.append('codex logout')
    elif codex: tt = '⚠️ chưa đăng nhập'
    lenh.append('codex login')
    ban.append('trên trình duyệt chọn "Sign in with ChatGPT", đăng nhập tài khoản có gói Plus/Pro')
elif not any(l.split()[:1] == ['image_generation'] and l.split()[-1:] == ['true'] for l in chay([codex, 'features', 'list'])[1].splitlines()):
    tt = '⚠️ Codex chưa bật công cụ vẽ'; lenh += CAI_NODE + [CAI_CODEX]
bang.append(('1. Gói ChatGPT — Codex tự vẽ (ảnh đẹp nhất đã đo)', '0đ thêm, trừ hạn mức gói ChatGPT Plus/Pro (~35 nghìn token gói/ảnh)', tt, lenh, ban))

# --- 2. Gói Google AI Pro/Ultra qua Antigravity CLI (công cụ generate_image có sẵn)
agy = tim('agy', os.path.join(NHA, '.local', 'bin', 'agy'), os.path.join(LOCALAPPDATA, 'agy', 'bin', 'agy.exe'))
ma_agy, ra_agy = chay([agy, 'models'], cho=40) if agy else (-1, '')
if not agy: tt, lenh, ban = '⚠️ chưa cài', [MO_TRANG + 'https://antigravity.google/download'], [
    'tải + cài Antigravity, đăng nhập tài khoản Google có gói AI Pro/Ultra, bật công cụ dòng lệnh `agy` theo hướng dẫn trong ứng dụng']
elif ma_agy != 0 or 'gemini' not in ra_agy: tt, lenh, ban = '⚠️ chưa đăng nhập', ['agy'], ['đăng nhập tài khoản Google có gói AI Pro/Ultra trong cửa sổ agy']
else: tt, lenh, ban = '✅ đã nối', [], []
bang.append(('2. Gói Gemini (Google AI Pro) — Antigravity tự vẽ', '0đ thêm, trừ hạn mức vẽ ảnh của gói (trần TUẦN riêng)', tt, lenh, ban))

# --- 3. Claude tự dựng bằng code: ảnh thật của hãng cắt nền + nền vẽ bằng code + chữ HTML (không AI vẽ)
tach = 'Vision của Mac' if mac and not WIN and chay(['xcode-select', '-p'])[0] == 0 else 'máy tách nền đơn giản (ảnh hãng phải nền trắng/trơn)'
bang.append(('3. Claude tự dựng bằng code (đúng 100% sản phẩm, kiểu ảnh đồ hoạ, không có cảnh chụp)', '0đ',
             ('✅ sẵn sàng · tách nền bằng ' + tach) if nen_ok else '⚠️ cài máy nền trước', [], []))

# ===== TẦNG 2 — máy vẽ các hãng qua API: miễn phí trước, trả tiền sau (CHỈ khi bạn tự chọn)
# --- 4. Seedream 4.5 qua BytePlus ModelArk (ByteDance): 200 ảnh miễn phí
co_bp = bool(os.environ.get('ARK_API_KEY')) or co_khoa_keyring('byteplus') or (os.path.exists(KHOA_BYTEPLUS) and os.path.getsize(KHOA_BYTEPLUS) > 20) \
    or (mac and chay(['security', 'find-generic-password', '-s', 'byteplus-ark-claude-thu-anh'])[0] == 0)
bang.append(('4. Seedream 4.5 (BytePlus, hãng ByteDance) — ảnh thứ 2 sau ChatGPT', '200 ảnh miễn phí; sau đó ~0,04 USD/ảnh. Cần thẻ Visa/Master hoặc PayPal để KÍCH HOẠT (chưa trừ tiền)',
             '✅ đã có khoá' if co_bp else '⚠️ chưa có khoá',
             [] if co_bp else [MO_TRANG + 'https://console.byteplus.com/ark/region:ap-southeast-1/openManagement', KIEM_RIENG + ' --nhap-khoa byteplus'],
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
             CAI_NODE + ([] if da_cf else [f'{NPX} --yes wrangler@{WRANGLER_BAN} login']),
             BAN_NODE + ([] if da_cf else ['đăng nhập Cloudflare trên trình duyệt (chưa có thì đăng ký miễn phí), bấm "Allow"'])))

# --- 6. Trả tiền Gemini (Nano Banana 2.1)
co_khoa = bool(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')) or co_khoa_keyring('gemini') \
    or (os.path.exists(KHOA_GEMINI) and os.path.getsize(KHOA_GEMINI) > 20)
co_genai = os.path.exists(PY) and chay([PY, '-c', 'import google.genai'])[0] == 0
bang.append(('6. Gemini API trả tiền (Nano Banana 2.1)', '~0,05 USD/ảnh 2K (~0,25 USD/sản phẩm), trừ thẻ gắn với khoá Google — CHỈ khi bạn tự chọn',
             '✅ đã có khoá' if co_khoa and co_genai else '⚠️ chưa có khoá' if not co_khoa else '⚠️ thiếu thư viện',
             ([] if co_genai else [CAI_PIP + f'"{os.path.join(GOC, "khoa-thu-vien-gemini.txt")}"'])
             + ([] if co_khoa else [MO_TRANG + 'https://aistudio.google.com/apikey', KIEM_RIENG + ' --nhap-khoa gemini']),
             [] if co_khoa else ['tạo khoá + gắn thẻ thanh toán trên trang Google', 'dán khoá vào hộp nhập kín hiện lên (khoá vào kho khoá của máy; KHÔNG dán vào chat)']))


# ===== TẦNG 3 — công cụ làm ảnh chuyên nghiệp
bang.append(('7. Công cụ chuyên nghiệp bạn ĐÃ dùng (Photoroom, Pebblely, Canva…)', 'theo gói bạn đang trả',
             '— nói tên công cụ, Agent dùng tài khoản/khoá của bạn', [], []))

TU_MAY.update(l for b in bang for l in b[3] if l.startswith((KIEM, KIEM_RIENG)))
print('# Công cụ vẽ trên máy này — xếp theo thứ tự nên dùng\n(Tầng 1: gói AI bạn đang trả · Tầng 2: máy vẽ qua API · Tầng 3: công cụ chuyên nghiệp)\n'
      '(mọi đường: phần Agent chạy trừ hạn mức gói Agent của bạn, ~120 nghìn token/sản phẩm)\n')
print('| Công cụ | Tiền | Trên máy bạn |\n|---|---|---|')
for ten, tien, tt, _, _ in bang: print(f'| {ten} | {tien} | {tt} |')
chua = [b for b in bang if b[2].startswith('⚠️') and (b[3] or b[4])]
if chua:
    print('\n## Chọn rồi mà chưa sẵn sàng: Agent cho người dùng xem danh sách sẽ cài, HỎI ĐỒNG Ý, rồi mới chạy; bạn làm phần của bạn')
    for ten, _, _, lenh, ban in chua:
        print(f'\n**{ten}**')
        for l in lenh:
            print(f'- Agent chạy: `{l if l in TU_MAY else TIEN_TO + l}`')
        for l in ban: print(f'- Bạn làm: {l}')
