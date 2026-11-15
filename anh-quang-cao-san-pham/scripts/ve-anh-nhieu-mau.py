# Vẽ 1 ảnh TRẢ TIỀN bằng Gemini (mặc định Nano Banana 2.1, ~0,05 USD/ảnh 2K), kèm NHIỀU ảnh mẫu chính hãng.
# Muốn 0đ: dùng ve-anh-mien-phi.py (Cloudflare Workers AI). Máy đắt gemini-3-pro-image chỉ khi cần giữ logo/chữ nhỏ.
# Khoá đọc theo thứ tự: biến GEMINI_API_KEY (hoặc GOOGLE_API_KEY) → kho khoá hệ điều hành (keyring, service anh-qc, tên gemini;
# do `kiem-cong-cu-ve.py --nhap-khoa gemini` ghi qua ô kín) → tệp cũ ~/.config/anh-qc/gemini.key (chỉ đọc). Máy KHÔNG in khoá ra.
# Có trần tiền: cộng sổ chi trong thư mục ảnh ra, chạm --tran-usd thì dừng, không vẽ.
# Cài 1 lần: xem dòng "Cài 1 lần" trong SKILL.md (môi trường riêng, khoá phiên bản).
# Chạy:  python ve-anh-nhieu-mau.py --loi-nho loi-nho.txt --mau a.jpg b.jpg --ti-le 4:5 --co 2K --ra ve/canh-1-a.png
# Vẽ LẦN LƯỢT, đừng chạy 2 lệnh vẽ song song (sổ tiền không khoá, có thể vượt trần).
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, json, os, re, sys, time

# USD/ảnh theo bảng giá ai.google.dev/gemini-api/docs/pricing (đọc 14/11/2026). Gemini KHÔNG có lượt vẽ ảnh miễn phí.
BANG_GIA = {'gemini-nano-banana-2.1': {'1K': 0.0336, '2K': 0.0504, '4K': 0.113},
            'gemini-3-pro-image': {'1K': 0.134, '2K': 0.134, '4K': 0.24}}

ap = argparse.ArgumentParser(description='Vẽ ảnh có sản phẩm thật, kèm ảnh mẫu chính hãng')
ap.add_argument('--loi-nho', required=True, help='tệp chữ lời nhờ vẽ')
ap.add_argument('--mau', nargs='*', default=[], help='ảnh mẫu chính hãng (2–4 ảnh cùng góc nhất)')
ap.add_argument('--ti-le', default='4:5', help='1:1 · 4:5 · 9:16 · 16:9 · 3:4 · 4:3')
ap.add_argument('--co', default='2K', choices=['1K', '2K', '4K'], help='cỡ ảnh')
ap.add_argument('--ra', required=True, help='đường dẫn ảnh ra (.png)')
ap.add_argument('--model', default='gemini-nano-banana-2.1', choices=list(BANG_GIA))
ap.add_argument('--tran-usd', type=float, default=5.0, help='trần tiền cho cả thư mục ảnh ra')
a = ap.parse_args()
GIA = BANG_GIA[a.model]

thu_muc = os.path.dirname(os.path.abspath(a.ra)); os.makedirs(thu_muc, exist_ok=True)
so = os.path.join(thu_muc, 'so-chi.jsonl')
da_tieu = 0.0
if os.path.exists(so):
    for dong in open(so, encoding='utf-8'):
        try:
            d = json.loads(dong); da_tieu += d.get('usd', 0) if d.get('ok') else 0
        except ValueError:
            pass
if da_tieu + GIA[a.co] > a.tran_usd:
    sys.exit(f'DỪNG: đã tiêu {da_tieu:.2f} USD, vẽ thêm sẽ quá trần {a.tran_usd} USD. Hỏi người dùng nâng trần (--tran-usd).')

khoa = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not khoa:
    try:
        import keyring  # kho khoá của hệ điều hành (Mac Keychain / Windows Credential Manager)
        khoa = keyring.get_password('anh-qc', 'gemini')
    except Exception:  # chưa cài keyring hoặc máy không có kho khoá ⇒ thử chỗ lưu của bản cũ
        khoa = None
tep_khoa = os.path.expanduser('~/.config/anh-qc/gemini.key')  # chỗ lưu của bản cũ: chỉ đọc
if not khoa and os.path.exists(tep_khoa):
    with open(tep_khoa, encoding='utf-8-sig') as f: khoa = f.read()
if not khoa:
    sys.exit('THIẾU KHOÁ: chạy `kiem-cong-cu-ve.py --nhap-khoa gemini` bằng Python riêng của skill để người dùng dán khoá vào ô kín (lấy ở aistudio.google.com/apikey). Không dán khoá vào chat.')
khoa = khoa.strip()
if not re.fullmatch(r'[\x21-\x7e]{20,200}', khoa):  # khoá thật không có dấu cách; chuỗi lỗi bị nạp nhầm thì có
    sys.exit('KHOÁ KHÔNG HỢP LỆ: biến khoá có dấu cách / quá ngắn — có thể đã nạp nhầm 1 dòng báo lỗi. Kiểm lại cách nạp khoá.')

from google import genai
from google.genai import types

phan = [open(a.loi_nho, encoding='utf-8').read()]
for r in a.mau:
    phan.append(types.Part.from_bytes(data=open(r, 'rb').read(),
                                      mime_type='image/png' if r.lower().endswith('.png') else 'image/jpeg'))
cfg = types.GenerateContentConfig(response_modalities=['IMAGE'],
                                  image_config=types.ImageConfig(aspect_ratio=a.ti_le, image_size=a.co))
t = time.time(); ok = False; loi = ''
try:
    cli = genai.Client(api_key=khoa)  # giữ biến: client tạm bị dọn rác sẽ đóng kết nối ("client has been closed")
    resp = cli.models.generate_content(model=a.model, contents=phan, config=cfg)
    for p in resp.candidates[0].content.parts:
        if getattr(p, 'inline_data', None) and p.inline_data.data:
            open(a.ra, 'wb').write(p.inline_data.data); ok = True; break
    if not ok:
        loi = 'không có ảnh: ' + str(getattr(resp.candidates[0], 'finish_reason', ''))
except Exception as e:  # lỗi mạng / hết hạn mức / sai tên model
    loi = str(e).replace(khoa, '***')[:300]
with open(so, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'luc': time.strftime('%Y-%m-%d %H:%M:%S'), 'model': a.model, 'co': a.co, 'ra': a.ra,
                        'ok': ok, 'usd': GIA[a.co] if ok else 0, 'giay': round(time.time() - t), 'loi': loi},
                       ensure_ascii=False) + '\n')
print(f'OK {a.ra} · đã tiêu {da_tieu + (GIA[a.co] if ok else 0):.2f}/{a.tran_usd} USD' if ok else 'LỖI ' + loi)
