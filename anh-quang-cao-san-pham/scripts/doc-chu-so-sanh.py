# Máy đọc chữ soát nhãn: đọc chữ (Mac: Apple Vision · Windows: Windows.Media.Ocr qua gói PyWinRT — đều có sẵn trong máy, 0đ) trên ảnh hãng và ảnh vẽ, báo chữ/số quan trọng của hãng mà ảnh vẽ mất/sai.
# Mỗi ảnh: cắt vùng sản phẩm (nếu có) → phóng ×2 → đọc. So khớp KHÔNG phân biệt hoa/thường, khoảng trắng tuỳ ý ("336g" = "336 g"), GIỮ dấu tiếng Việt, có ranh giới ("336 g" ≠ "1336 g").
# Kết luận từng chữ: ĐẠT (có ở cả 2) · TRƯỢT (ảnh hãng có, ảnh vẽ không) · MÁY KHÔNG ĐỌC ĐƯỢC (ảnh hãng cũng không thấy → phóng to soát mắt).
# Thoát mã 2 nếu có TRƯỢT. Hệ khác (Linux) → báo soát mắt, thoát 0.
# Windows: ưu tiên bộ đọc vi-VN; máy chưa có gói tiếng Việt → dùng bộ có sẵn (thường en-US) và SO KHÔNG DẤU cả 2 phía (dấu soát mắt).   Đo 15/11/2026: bắt được "336 g" → "136 g" của Seedream.
# Chạy: ~/.venv-anh-qc/bin/python doc-chu-so-sanh.py --hang hang.jpg --ve ve.png
#       --chu "336 g" "3in1" "CÀ PHÊ HÒA TAN" [--vung-ve x0,y0,x1,y1] [--vung-hang x0,y0,x1,y1]   (vùng theo tỉ lệ 0–1)
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, os, re, sys, tempfile, unicodedata

ap = argparse.ArgumentParser(description='Soát chữ trên nhãn: ảnh hãng vs ảnh vẽ (Apple Vision)')
ap.add_argument('--hang', required=True); ap.add_argument('--ve', required=True)
ap.add_argument('--chu', nargs='+', required=True, help='chữ/số quan trọng phải còn nguyên')
ap.add_argument('--vung-ve', default=''); ap.add_argument('--vung-hang', default='')
a = ap.parse_args()
if sys.platform not in ('darwin', 'win32'):
    print('Máy đọc chữ chỉ chạy trên Mac và Windows — soát mắt bằng cat-phong-to.py'); sys.exit(0)
from PIL import Image, ImageOps


def chuan(s): return re.sub(r'\s+', '', unicodedata.normalize('NFC', s).lower())  # bỏ khoảng trắng, giữ dấu


def co(c, van):  # chữ c có trong văn bản đọc được: khoảng trắng giữa ký tự tuỳ ý, trước/sau không dính chữ hay số
    van = unicodedata.normalize('NFC', van).lower()
    return re.search(r'(?<!\w)' + r'\s*'.join(re.escape(k) for k in chuan(c)) + r'(?!\w)', van) is not None


def bo_dau(s):  # bỏ dấu tiếng Việt (cả đ/Đ) — dùng khi bộ đọc của máy không có tiếng Việt
    s = unicodedata.normalize('NFD', s.replace('đ', 'd').replace('Đ', 'D'))
    return unicodedata.normalize('NFC', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


def doc_mac(p):
    import Quartz, Vision
    from Foundation import NSURL
    src = Quartz.CGImageSourceCreateWithURL(NSURL.fileURLWithPath_(p), None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setUsesLanguageCorrection_(False); req.setRecognitionLanguages_(['vi-VT', 'en-US'])
    ok, _ = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None).performRequests_error_([req], None)
    return [o.topCandidates_(1)[0].string() for o in (req.results() or [])] if ok else []


_ENGINE = {}  # Windows: tạo bộ đọc 1 lần (ưu tiên vi-VN)


def engine_win():
    if not _ENGINE:
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
        e = OcrEngine.try_create_from_language(Language('vi-VN'))
        _ENGINE['vi'] = e is not None
        _ENGINE['e'] = e or OcrEngine.try_create_from_user_profile_languages()
    return _ENGINE['e']


def doc_win(p):
    import asyncio
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.graphics.imaging import BitmapDecoder, BitmapPixelFormat, BitmapAlphaMode
    from winrt.windows.storage import StorageFile, FileAccessMode
    e = engine_win()
    if e is None: sys.exit('LỖI máy Windows này chưa có bộ đọc chữ nào (Cài đặt → Ngôn ngữ → thêm ngôn ngữ). Soát mắt bằng cat-phong-to.py.')

    async def chay():
        tep = await StorageFile.get_file_from_path_async(os.path.abspath(p))
        dong = await tep.open_async(FileAccessMode.READ)
        bm = await (await BitmapDecoder.create_async(dong)).get_software_bitmap_async(BitmapPixelFormat.BGRA8, BitmapAlphaMode.PREMULTIPLIED)
        return [l.text for l in (await e.recognize_async(bm)).lines]
    return asyncio.run(chay())


def doc(duong, vung):
    im = ImageOps.exif_transpose(Image.open(duong)).convert('RGB'); W, H = im.size
    if vung:
        x0, y0, x1, y1 = (float(v) for v in vung.split(','))
        im = im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    if sys.platform == 'win32':  # Windows.Media.Ocr từ chối ảnh quá cỡ (OcrEngine.MaxImageDimension, thường 2600) ⇒ thu nhỏ vừa khung
        try:
            from winrt.windows.media.ocr import OcrEngine
            gioi = int(OcrEngine.max_image_dimension)
        except (ImportError, AttributeError, TypeError, ValueError): gioi = 2600
        if max(im.size) > gioi:
            k = gioi / max(im.size); im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    with tempfile.TemporaryDirectory() as tam:
        p = os.path.join(tam, 'v.png'); im.save(p)
        return doc_win(p) if sys.platform == 'win32' else doc_mac(p)

if sys.platform == 'win32':
    try: engine_win()
    except ImportError as e:
        print(f'Máy đọc chữ Windows thiếu gói PyWinRT ({e.name}) — chạy scripts/kiem-cong-cu-ve.py để cài; tạm thời soát mắt bằng cat-phong-to.py'); sys.exit(0)
hang, ve = doc(a.hang, a.vung_hang), doc(a.ve, a.vung_ve)
KHONG_DAU = sys.platform == 'win32' and not _ENGINE.get('vi')
if KHONG_DAU:
    print('máy Windows chưa có gói đọc tiếng Việt: so không dấu, dấu soát mắt. '
          'Thêm gói: Cài đặt → Thời gian & ngôn ngữ → Ngôn ngữ & khu vực → thêm Tiếng Việt (nhớ tick "Nhận dạng chữ viết"), rồi chạy lại.\n')
    hang, ve = [bo_dau(d) for d in hang], [bo_dau(d) for d in ve]
    a.chu = [bo_dau(c) for c in a.chu]
nh = chuan(' '.join(hang))
print(f'Máy đọc được {len(hang)} dòng chữ ở ảnh hãng, {len(ve)} dòng ở ảnh vẽ.\n')
print(f'{"chữ quan trọng":<24}{"ảnh hãng":<12}{"ảnh vẽ":<10}kết luận')
truot = 0
for c in a.chu:
    h, v = co(c, ' '.join(hang)), co(c, ' '.join(ve))
    kl = 'ĐẠT' if h and v else 'TRƯỢT' if h else 'MÁY KHÔNG ĐỌC ĐƯỢC (phóng to soát mắt)'
    truot += kl == 'TRƯỢT'
    print(f'{c:<24}{"thấy" if h else "không":<12}{"thấy" if v else "không":<10}{kl}')
lạ = sorted({chuan(w) for d in ve for w in re.findall(r'\w+', d) if len(w) >= 3 and not w.isdigit() and chuan(w) not in nh})
print('\nChữ lạ trên ảnh vẽ (ảnh hãng không có — gợi ý chữ AI bịa, soát mắt):', ', '.join(lạ[:40]) or 'không có')
print(f'\n{"CÓ " + str(truot) + " chữ TRƯỢT — ảnh vẽ sai/mất chữ hãng" if truot else "Không chữ nào TRƯỢT"}')
sys.exit(2 if truot else 0)
