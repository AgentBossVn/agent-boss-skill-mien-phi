# Kiểm trên máy người dùng: đã có / đã nối những công cụ vẽ nào, mỗi công cụ tốn tiền gì, chọn rồi thì Agent làm gì.
# Agent chạy máy này ở Bước 0, đưa bảng cho người dùng chọn. Chọn xong mà chưa sẵn sàng → Agent TỰ chạy các dòng
# "Agent chạy" (lệnh mở trình duyệt / chờ người bấm thì chạy nền); người dùng chỉ làm dòng "Bạn làm".
# Cài xong chạy lại máy này, thấy ✅ mới vẽ. Máy CHỈ ĐỌC (trừ --nhap-khoa), KHÔNG in khoá / token ra.
# Chạy:  python3 kiem-cong-cu-ve.py              → bảng công cụ
#        python3 kiem-cong-cu-ve.py --nhap-khoa [gemini|byteplus] → hiện ô kín cho người dùng dán khoá, lưu ~/.config/anh-qc/<tên>.key
#          (Windows: không có ô kín — máy mở Notepad vào đúng tệp khoá, người dùng dán khoá, lưu, đóng)
# Windows (16/11/2026): máy in lệnh PowerShell, môi trường Python riêng ở %USERPROFILE%\.venv-anh-qc\Scripts\python.exe, cài bằng uv;
#   máy đọc chữ = Windows.Media.Ocr qua gói PyWinRT; Codex/Antigravity cài bằng trình cài chính thức (không cần quyền quản trị).
# Bản 3 (15/11/2026): Tầng 1 gói AI bạn ĐANG TRẢ (ChatGPT, Gemini, Claude) → Tầng 2 máy vẽ các hãng qua API
#   (miễn phí trước, rồi trả tiền) → Tầng 3 công cụ làm ảnh chuyên nghiệp bạn đã dùng sẵn.
#        python3 kiem-cong-cu-ve.py --cai-brew   → mở cửa sổ Terminal chạy trình cài Homebrew chính thức; người dùng gõ mật khẩu máy
#          ở ĐÓ (Agent không có ô gõ mật khẩu, không đụng mật khẩu).
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import os, shutil, socket, subprocess, sys

NHA = os.path.expanduser('~')
WIN = sys.platform == 'win32'
APPDATA, LOCALAPPDATA = os.environ.get('APPDATA', ''), os.environ.get('LOCALAPPDATA', '')
KHOA = {'gemini': ('Gemini API (bắt đầu bằng AIza…)', os.path.join(NHA, '.config', 'anh-qc', 'gemini.key')),
        'byteplus': ('BytePlus ModelArk (trang API Key)', os.path.join(NHA, '.config', 'anh-qc', 'byteplus.key'))}
KHOA_GEMINI, KHOA_BYTEPLUS = KHOA['gemini'][1], KHOA['byteplus'][1]
PY = os.path.join(NHA, '.venv-anh-qc', 'Scripts', 'python.exe') if WIN else os.path.join(NHA, '.venv-anh-qc', 'bin', 'python')  # môi trường riêng của skill (dòng "Cài 1 lần" trong SKILL.md)
CAI_BREW = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
CAI_UV = 'irm https://astral.sh/uv/install.ps1 | iex' if WIN else 'curl -LsSf https://astral.sh/uv/install.sh | sh'  # cài vào ~/.local/bin, không cần mật khẩu / quyền quản trị
# Phiên Agent không tự có đường tới công cụ vừa cài ⇒ mọi lệnh in ra đều kèm tiền tố này
TIEN_TO = ('$env:Path = "$env:USERPROFILE\\.local\\bin;$env:LOCALAPPDATA\\Programs\\OpenAI\\Codex\\bin;$env:LOCALAPPDATA\\agy\\bin;$env:APPDATA\\npm;$env:ProgramFiles\\nodejs;" + $env:Path; '
           if WIN else 'export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"; ')
PYTHON_KHOI = 'python' if WIN else 'python3'  # lệnh chạy chính máy này (Windows: python, không có python3)
KIEM = PYTHON_KHOI + (' scripts\\kiem-cong-cu-ve.py' if WIN else ' scripts/kiem-cong-cu-ve.py')
NPM, NPX = ('npm.cmd', 'npx.cmd') if WIN else ('npm', 'npx')  # PowerShell chặn npm.ps1 khi chính sách mặc định ⇒ gọi .cmd
GOI_PY = 'pillow==13.0.0 numpy==2.5.4 scipy==1.18.1 requests==2.34.2'
GOI_WIN = ' winrt-runtime==4.1.0 ' + ' '.join(f'winrt-Windows.{t}==4!10.0.28000.2957' for t in (
    'Media.Ocr', 'Graphics.Imaging', 'Storage', 'Storage.Streams', 'Globalization', 'Foundation', 'Foundation.Collections'))
CAI_PIP = ('uv pip install --python "$env:USERPROFILE\\.venv-anh-qc\\Scripts\\python.exe" ' if WIN else '~/.venv-anh-qc/bin/pip install ')
MO_TRANG = 'Start-Process ' if WIN else 'open '


def chay(lenh, cho=20):
    try:
        p = subprocess.run(lenh, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=cho, stdin=subprocess.DEVNULL)
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


if '--nhap-khoa' in sys.argv:
    loai = next((a for a in sys.argv if a in KHOA), 'gemini'); nhan, tep = KHOA[loai]
    if WIN:  # không có ô kín: mở Notepad vào đúng tệp, người dùng dán khoá, lưu, đóng
        os.makedirs(os.path.dirname(tep), exist_ok=True)
        if not os.path.exists(tep): open(tep, 'w', encoding='utf-8').close()
        subprocess.Popen(['notepad.exe', tep])
        print(f'Đã mở Notepad vào {tep}. Bạn làm: dán khoá {nhan} vào, bấm Ctrl+S rồi đóng Notepad (khoá chỉ nằm trên máy này, KHÔNG dán vào chat).'); sys.exit(0)
    if sys.platform != 'darwin': sys.exit('Ô kín chỉ có trên Mac. Máy khác: người dùng tự dán khoá vào tệp ' + tep)
    ma, ra = chay(['osascript', '-e', 'activate', '-e', f'text returned of (display dialog "Dán khoá {nhan} rồi bấm OK. '
                   'Khoá chỉ lưu trên máy này." default answer "" with hidden answer with title "Ảnh quảng cáo")'], cho=600)
    khoa = ra.strip() if ma == 0 else ''
    if not khoa or ' ' in khoa: sys.exit('Chưa lưu: ô trống hoặc người dùng bấm Huỷ.')
    os.makedirs(os.path.dirname(tep), mode=0o700, exist_ok=True)
    with os.fdopen(os.open(tep, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f: f.write(khoa + '\n')
    os.chmod(tep, 0o600)
    print(f'Đã lưu khoá vào {tep} (chỉ tài khoản máy này đọc được, không in ra).'); sys.exit(0)

if '--cai-brew' in sys.argv:
    if sys.platform != 'darwin': sys.exit('Chỉ dùng trên Mac (Windows không cần Homebrew).')
    lenh_as = CAI_BREW.replace('\\', '\\\\').replace('"', '\\"')  # đặt lệnh vào chuỗi AppleScript
    ma, ra = chay(['osascript', '-e', 'tell application "Terminal"', '-e', 'activate', '-e', f'do script "{lenh_as}"', '-e', 'end tell'])
    if ma != 0: sys.exit('Không mở được Terminal: ' + ra.strip()[:200])
    print('Đã mở cửa sổ Terminal chạy trình cài Homebrew. Người dùng: gõ mật khẩu máy (gõ không hiện ký tự) rồi Enter; '
          'thấy "Press RETURN" thì Enter; chờ chữ "Installation successful" (5–15 phút). Xong chạy lại máy kiểm.'); sys.exit(0)

mac = sys.platform == 'darwin'
brew = None if WIN else tim('brew', '/opt/homebrew/bin/brew', '/usr/local/bin/brew')
CAI_BREW_TRUOC = [] if brew or WIN else [KIEM + ' --cai-brew']
BAN_BREW = [] if brew or WIN else ['trong cửa sổ Terminal vừa mở: gõ mật khẩu máy (gõ không hiện ký tự) → Enter, chờ chữ "Installation successful"']
uv = tim('uv', os.path.join(NHA, '.local', 'bin', 'uv.exe' if WIN else 'uv'))
CAI_UV_TRUOC = [] if uv else [CAI_UV]
node = tim('npm', '/opt/homebrew/bin/npm', '/usr/local/bin/npm', os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'))
CAI_NODE = [] if node else (['winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements'] if WIN
                            else CAI_BREW_TRUOC + ['brew install node'])
BAN_NODE = [] if node else (['nếu hiện hộp xin quyền (UAC) thì bấm Yes'] if WIN else BAN_BREW)
bang = []  # (tên, tiền, trạng thái, lệnh Agent chạy, việc bạn làm)

# --- Máy nền: mọi đường đều cần (soát, dán nhãn, đặt chữ)
lenh, ban = [], []
THU_VIEN = 'import PIL, numpy, scipy, requests' + (', Vision' if sys.platform == 'darwin' else ', winrt.windows.media.ocr' if WIN else '')
if not (os.path.exists(PY) and chay([PY, '-c', THU_VIEN])[0] == 0):
    # python3 sẵn của Apple là 3.9 ⇒ không cài nổi bản thư viện đã ghim (cần ≥ 3.12) ⇒ uv tự tải Python 3.12 riêng
    lenh += CAI_UV_TRUOC + ([('uv venv --seed --python 3.12 "$env:USERPROFILE\\.venv-anh-qc"' if WIN else 'uv venv --seed --python 3.12 ~/.venv-anh-qc')] if not os.path.exists(PY) else [])
    lenh.append(CAI_PIP + GOI_PY + (' pyobjc-framework-Vision==13.0 pyobjc-framework-Quartz==13.0' if sys.platform == 'darwin' else GOI_WIN if WIN else ''))
if not tim_trinh_duyet():  # Chrome hoặc Edge đều được (Windows luôn có Edge)
    if WIN:
        lenh += ['winget install --id Google.Chrome -e --accept-package-agreements --accept-source-agreements']; ban += ['nếu hiện hộp xin quyền (UAC) thì bấm Yes']
    else:
        lenh += CAI_BREW_TRUOC + ['brew install --cask google-chrome']; ban += BAN_BREW
bang.append(('Máy nền (đường nào cũng cần: soát, đọc chữ, dán nhãn, đặt chữ)', '0đ', '⚠️ thiếu' if lenh else '✅ sẵn sàng', lenh, ban))
nen_ok = not lenh

# ===== TẦNG 1 — gói AI bạn ĐANG TRẢ: Agent của gói đó tự vẽ, 0đ thêm
# --- 1. Gói ChatGPT qua Codex
CAI_CODEX_WIN = 'irm https://chatgpt.com/codex/install.ps1 | iex'  # trình cài chính thức, vào %LOCALAPPDATA%\\Programs\\OpenAI\\Codex\\bin, không cần Node / quyền quản trị
codex = tim('codex', '/opt/homebrew/bin/codex', '/usr/local/bin/codex', os.path.join(LOCALAPPDATA, 'Programs', 'OpenAI', 'Codex', 'bin', 'codex.exe'),
            os.path.join(APPDATA, 'npm', 'codex.cmd'))
lenh, ban, tt = ([] if WIN else list(CAI_NODE)), ([] if WIN else list(BAN_NODE)), '✅ đã nối'
if not codex: lenh.append(CAI_CODEX_WIN if WIN else 'npm i -g @openai/codex'); tt = '⚠️ chưa cài'
dang_nhap = chay([codex, 'login', 'status'])[1] if codex else ''
if 'ChatGPT' not in dang_nhap:
    if 'API key' in dang_nhap: tt = '⚠️ đang đăng nhập bằng KHOÁ API (vẽ sẽ TÍNH TIỀN OpenAI)'; lenh.append('codex logout')
    elif codex: tt = '⚠️ chưa đăng nhập'
    lenh.append('codex login')
    ban.append('trên trình duyệt chọn "Sign in with ChatGPT", đăng nhập tài khoản có gói Plus/Pro')
elif not any(l.split()[:1] == ['image_generation'] and l.split()[-1:] == ['true'] for l in chay([codex, 'features', 'list'])[1].splitlines()):
    tt = '⚠️ Codex chưa bật công cụ vẽ'; lenh.append(CAI_CODEX_WIN if WIN else 'npm i -g @openai/codex@latest')
bang.append(('1. Gói ChatGPT — Codex tự vẽ (ảnh đẹp nhất đã đo)', '0đ thêm, trừ hạn mức gói ChatGPT Plus/Pro (~35 nghìn token gói/ảnh)', tt, lenh, ban))

# --- 2. Gói Google AI Pro/Ultra qua Antigravity CLI (công cụ generate_image có sẵn)
agy = tim('agy', os.path.join(NHA, '.local', 'bin', 'agy'), os.path.join(LOCALAPPDATA, 'agy', 'bin', 'agy.exe'))
ma_agy, ra_agy = chay([agy, 'models'], cho=40) if agy else (-1, '')
if not agy and WIN: tt, lenh, ban = '⚠️ chưa cài', ['irm https://antigravity.google/cli/install.ps1 | iex', 'agy'], [
    'đăng nhập tài khoản Google có gói AI Pro/Ultra trong cửa sổ agy']  # trình cài chính thức: %LOCALAPPDATA%\\agy\\bin\\agy.exe
elif not agy: tt, lenh, ban = '⚠️ chưa cài', ['open https://antigravity.google/download'], [
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
co_bp = bool(os.environ.get('ARK_API_KEY')) or (os.path.exists(KHOA_BYTEPLUS) and os.path.getsize(KHOA_BYTEPLUS) > 20) \
    or (mac and chay(['security', 'find-generic-password', '-s', 'byteplus-ark-claude-thu-anh'])[0] == 0)
bang.append(('4. Seedream 4.5 (BytePlus, hãng ByteDance) — ảnh thứ 2 sau ChatGPT', '200 ảnh miễn phí; sau đó ~0,04 USD/ảnh. Cần thẻ Visa/Master hoặc PayPal để KÍCH HOẠT (chưa trừ tiền)',
             '✅ đã có khoá' if co_bp else '⚠️ chưa có khoá',
             [] if co_bp else [MO_TRANG + 'https://console.byteplus.com/ark/region:ap-southeast-1/openManagement', KIEM + ' --nhap-khoa byteplus'],
             [] if co_bp else ['đăng ký BytePlus, BẬT "Free Credits Only Mode" (chỉ dùng phần miễn phí), thêm thẻ/PayPal, bấm Activate dòng Seedream 4.5',
                               'trang API Key → Create → dán khoá vào ' + ('Notepad vừa mở, Ctrl+S rồi đóng' if WIN else 'ô kín hiện lên') + ' (KHÔNG dán vào chat)']))

# --- 5. Cloudflare Workers AI, phần miễn phí hằng ngày
cf = [os.path.join(NHA, 'Library', 'Preferences', '.wrangler', 'config', 'default.toml'),
      os.path.join(APPDATA, 'xdg.config', '.wrangler', 'config', 'default.toml'),
      os.path.join(os.environ.get('XDG_CONFIG_HOME') or os.path.join(NHA, '.config'), '.wrangler', 'config', 'default.toml')]
da_cf = any(os.path.exists(f) and 'oauth_token' in open(f, encoding='utf-8', errors='ignore').read() for f in cf) \
    or bool(os.environ.get('CLOUDFLARE_API_TOKEN') and os.environ.get('CLOUDFLARE_ACCOUNT_ID'))
with socket.socket() as s: s.settimeout(1); cong_bat = s.connect_ex(('127.0.0.1', 8841)) == 0
bang.append(('5. Cloudflare — miễn phí, ảnh kém nhất', '0đ trong ~40 ảnh/ngày; quá mức máy tự dừng, không tính tiền',
             ('✅ đã nối · ' + ('cổng vẽ đang bật' if cong_bat else 'Agent bật cổng khi vẽ')) if da_cf and node else '⚠️ chưa nối',
             CAI_NODE + ([] if da_cf else [NPX + ' wrangler login']),
             BAN_NODE + ([] if da_cf else ['đăng nhập Cloudflare trên trình duyệt (chưa có thì đăng ký miễn phí), bấm "Allow"'])))

# --- 6. Trả tiền Gemini (Nano Banana 2.1)
co_khoa = bool(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')) \
    or (os.path.exists(KHOA_GEMINI) and os.path.getsize(KHOA_GEMINI) > 20)
co_genai = os.path.exists(PY) and chay([PY, '-c', 'import google.genai'])[0] == 0
bang.append(('6. Gemini API trả tiền (Nano Banana 2.1)', '~0,05 USD/ảnh 2K (~0,25 USD/sản phẩm), trừ thẻ gắn với khoá Google — CHỈ khi bạn tự chọn',
             '✅ đã có khoá' if co_khoa and co_genai else '⚠️ chưa có khoá' if not co_khoa else '⚠️ thiếu thư viện',
             ([] if co_genai else [CAI_PIP + 'google-genai==3.2.0'])
             + ([] if co_khoa else [MO_TRANG + 'https://aistudio.google.com/apikey', KIEM + ' --nhap-khoa gemini']),
             [] if co_khoa else ['tạo khoá + gắn thẻ thanh toán trên trang Google', 'dán khoá vào ' + ('Notepad vừa mở, Ctrl+S rồi đóng' if WIN else 'ô kín hiện lên') + ' (KHÔNG dán vào chat)']))


# ===== TẦNG 3 — công cụ làm ảnh chuyên nghiệp
bang.append(('7. Công cụ chuyên nghiệp bạn ĐÃ dùng (Photoroom, Pebblely, Canva…)', 'theo gói bạn đang trả',
             '— nói tên công cụ, Agent dùng tài khoản/khoá của bạn', [], []))

print('# Công cụ vẽ trên máy này — xếp theo thứ tự nên dùng\n(Tầng 1: gói AI bạn đang trả · Tầng 2: máy vẽ qua API · Tầng 3: công cụ chuyên nghiệp)\n'
      '(mọi đường: phần Agent chạy trừ hạn mức gói Agent của bạn, ~120 nghìn token/sản phẩm)\n')
print('| Công cụ | Tiền | Trên máy bạn |\n|---|---|---|')
for ten, tien, tt, _, _ in bang: print(f'| {ten} | {tien} | {tt} |')
chua = [b for b in bang if b[2].startswith('⚠️') and (b[3] or b[4])]
if chua:
    print('\n## Chọn rồi mà chưa sẵn sàng: Agent tự làm, bạn chỉ làm phần của bạn')
    for ten, _, _, lenh, ban in chua:
        print(f'\n**{ten}**')
        for l in lenh:
            if l.startswith(PYTHON_KHOI + ' scripts'):
                print(f'- Agent chạy: `{l}`' + (' — rồi CHỜ người dùng báo cài xong, chạy lại máy kiểm' if '--cai-brew' in l else ''))
            else: print(f'- Agent chạy: `{TIEN_TO}{l}`')
        for l in ban: print(f'- Bạn làm: {l}')
