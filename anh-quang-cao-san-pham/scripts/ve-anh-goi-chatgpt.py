# Vẽ 1 ảnh bằng GÓI ChatGPT (Plus/Pro…) qua Codex CLI — không trả thêm tiền, trừ vào hạn mức gói.
# Cần: cài Codex CLI (`npm i -g @openai/codex`) + đăng nhập bằng tài khoản ChatGPT (`codex login`).
# Máy gọi `codex exec` trong thư mục tạm TRỐNG, chế độ chỉ-đọc (Codex không sửa được file nào của bạn),
# đính ảnh mẫu hãng, nhờ công cụ vẽ ảnh có sẵn của Codex vẽ, rồi chép ảnh trong ~/.codex/generated_images/<mã phiên này>/ ra
# (chỉ đúng phiên này: Codex khác chạy cùng lúc không lẫn ảnh). Lỗi / hết lượt → in "LỖI …", thoát mã 1.
# Đo 14/11/2026: ~2–2,5 phút/ảnh, ~35 nghìn token gói/ảnh.
# Chạy: python ve-anh-goi-chatgpt.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.png --ti-le 4:5 --ra ve/canh-1-a.png
#       [--model gpt-5.6-sol]  (chỉ khi Codex báo model mặc định "not supported when using Codex with a ChatGPT account":
#        chọn 1 model trong ~/.codex/models_cache.json)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile, time

KHUNG = {'1:1': '1:1 square', '4:5': '4:5 portrait (e.g. 1080x1350)', '9:16': '9:16 tall portrait (e.g. 1080x1920)',
         '16:9': '16:9 wide landscape (e.g. 1920x1080)', '3:4': '3:4 portrait', '4:3': '4:3 landscape'}
ap = argparse.ArgumentParser(description='Vẽ ảnh bằng gói ChatGPT qua Codex CLI (0đ thêm)')
ap.add_argument('--loi-nho', required=True)
ap.add_argument('--mau', nargs='*', default=[], help='tối đa 4 ảnh mẫu chính hãng')
ap.add_argument('--ti-le', default='4:5', choices=list(KHUNG))
ap.add_argument('--ra', required=True)
ap.add_argument('--model', default='')
ap.add_argument('--cho', type=int, default=600, help='giây chờ tối đa')
a = ap.parse_args()
if len(a.mau) > 4: sys.exit('Tối đa 4 ảnh mẫu.')
codex = shutil.which('codex') or next((p for p in (os.path.expanduser('~/.local/bin/codex'), '/opt/homebrew/bin/codex',
         os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'OpenAI', 'Codex', 'bin', 'codex.exe'),
         os.path.join(os.environ.get('APPDATA', ''), 'npm', 'codex.cmd')) if os.path.exists(p)), '/opt/homebrew/bin/codex')
if not os.path.exists(codex): sys.exit('THIẾU Codex CLI: chạy kiem-cong-cu-ve.py, cài Codex theo dòng nó in (bản ghim), rồi `codex login` bằng tài khoản ChatGPT.')
kho = os.path.join(os.path.expanduser(os.environ.get('CODEX_HOME') or '~/.codex'), 'generated_images')
# Biến CODEX_API_KEY / OPENAI_API_KEY làm Codex vẽ bằng khoá API (TÍNH TIỀN) dù `login status` báo ChatGPT ⇒ bỏ khỏi môi trường gọi Codex
MOI_TRUONG = {k: v for k, v in os.environ.items() if k not in ('CODEX_API_KEY', 'OPENAI_API_KEY')}
if sys.platform != 'win32': MOI_TRUONG['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + os.path.expanduser('~/.local/bin') + ':' + os.environ.get('PATH', '')
try:  # đăng nhập bằng khoá API thì OpenAI TÍNH TIỀN từng ảnh ⇒ chỉ vẽ khi Codex đăng nhập bằng tài khoản ChatGPT
    dn = subprocess.run([codex, 'login', 'status'], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30, stdin=subprocess.DEVNULL, env=MOI_TRUONG)
    dn = dn.stdout + dn.stderr
except (OSError, subprocess.TimeoutExpired): dn = ''
if 'ChatGPT' not in dn:
    sys.exit('LỖI Codex không đăng nhập bằng tài khoản ChatGPT (khoá API sẽ TÍNH TIỀN) — chạy scripts/kiem-cong-cu-ve.py, làm theo dòng "Gói ChatGPT".')

loi = (f'Use your built-in image generation tool to generate exactly ONE photorealistic image, aspect ratio {KHUNG[a.ti_le]}. '
       'The attached photos are the official product photos: the product in the image must match them exactly '
       '(shape, proportions, colors, every part, label layout and label text). Do not write code, do not run commands, '
       'do not create files yourself — only generate the image, then reply with one short line.\n\nImage brief:\n'
       + open(a.loi_nho, encoding='utf-8').read())
lenh = [codex, 'exec', '--json', '--skip-git-repo-check', '-s', 'read-only', '-c', 'model_reasoning_effort="low"', '-c', 'notify=[]']
if a.model: lenh += ['-m', a.model]
for p in a.mau: lenh += ['-i', os.path.abspath(p)]
lenh += ['-']

os.makedirs(os.path.dirname(os.path.abspath(a.ra)) or '.', exist_ok=True)  # tạo trước: Codex lỗi vẫn ghi được sổ + báo lỗi
t0 = time.time(); ok = False; loi_bao = ''
with tempfile.TemporaryDirectory() as tam:  # thư mục trống: Codex không thấy kho nào của bạn
    try:
        p = subprocess.run(lenh, input=loi, cwd=tam, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=a.cho,
                           env=MOI_TRUONG)
        phien, loi_codex = '', []
        for dong in p.stdout.splitlines():  # --json: mỗi dòng 1 sự kiện; dòng đầu "thread.started" có mã phiên
            try: su = json.loads(dong)
            except ValueError: continue
            if su.get('type') == 'thread.started': phien = str(su.get('thread_id', ''))
            elif su.get('type') in ('error', 'turn.failed'):
                loi_codex.append(str(su.get('message') or (su.get('error') or {}).get('message') or su))
        # Codex lưu ảnh ở generated_images/<mã phiên>/ ⇒ chỉ lấy ảnh của ĐÚNG phiên này (phiên Codex khác chạy cùng lúc không lẫn vào)
        moi = sorted(glob.glob(os.path.join(kho, phien, '*.png')), key=os.path.getmtime) if re.fullmatch(r'[0-9a-fA-F-]{8,64}', phien) else []
        if moi:
            shutil.copy2(moi[-1], a.ra); ok = True
        else:
            dong = loi_codex or [d for d in p.stderr.splitlines() if 'ERROR' in d or 'limit' in d.lower()]
            loi_bao = (dong[-1] if dong else f'phiên {phien or "?"} không có ảnh (thoát {p.returncode})')[:300]
    except subprocess.TimeoutExpired:
        loi_bao = f'quá {a.cho} giây'
giay = round(time.time() - t0)


def co_anh(f):  # đọc rộng×cao từ đầu tệp PNG (không cần thư viện ảnh)
    try:
        with open(f, 'rb') as fh: b = fh.read(24)
        return f'{int.from_bytes(b[16:20], "big")}x{int.from_bytes(b[20:24], "big")}' if b[:8] == b'\x89PNG\r\n\x1a\n' else '?'
    except OSError: return '?'

so = os.path.join(os.path.dirname(os.path.abspath(a.ra)), 'so-chi.jsonl')
with open(so, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'luc': time.strftime('%Y-%m-%d %H:%M:%S'), 'duong': 'goi-chatgpt', 'model': a.model or 'mặc định',
                        'ti_le': a.ti_le, 'ra': a.ra, 'ok': ok, 'usd': 0, 'giay': giay, 'loi': loi_bao}, ensure_ascii=False) + '\n')
print(f'OK {a.ra} · {co_anh(a.ra)} · {giay} giây · 0đ (trừ hạn mức gói ChatGPT)' if ok else f'LỖI {loi_bao} · {giay} giây')
if not ok: sys.exit(1)
