# Bước 1: xem video đầu vào để agent chọn cảnh.
# Chạy: python3 scripts/phan_tich.py <video hoặc thư mục> [...] --ra <thư-mục-làm-việc> [--khong-nghe] [--khong-loc-bia] [--model large-v3-turbo]
# Ra: <thư-mục-làm-việc>/phan-tich/<tên>.json (độ dài, khung, chỗ lặng, chỗ đổi cảnh, lời nói theo từng chữ)
#     <thư-mục-làm-việc>/phan-tich/<tên>.jpg  (ảnh lưới: mỗi ô là 1 khung hình kèm giây, để agent nhìn và chọn đoạn đẹp)
import argparse, glob, json, os, re, subprocess, sys
from chung import run, thong_tin, ghi_json, tim_font, log  # nạp trước: tự đổi sang Python riêng
from PIL import Image, ImageDraw, ImageFont
from mau_tieng import vung_tieng

DUOI = ('.mp4', '.mov', '.m4v', '.mkv', '.webm', '.avi')
# câu máy nghe lời (Whisper) hay bịa ra ở chỗ không ai nói: học từ phụ đề video YouTube tiếng Việt (đo 18/11/2026 trên clip quay chó)
# dấu riêng của câu bịa (bỏ luôn); câu kết chung chung người thật cũng nói → chỉ bỏ khi cả đoạn chỉ có câu đó (≤ 10 chữ)
CAU_BIA = re.compile(r'subscribe|ghiền mì gõ|la la school', re.I)
CAU_KET = re.compile(r'đăng ký kênh|cảm ơn các bạn đã (theo dõi|xem)|hẹn gặp lại các bạn trong', re.I)


def cho_lang(path, nguong='-35dB', toi_thieu=0.3):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', f'silencedetect=noise={nguong}:d={toi_thieu}',
                          '-vn', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    st = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', err)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    if len(en) < len(st):  # lặng kéo tới hết video
        en.append(thong_tin(path)['dai'])
    return [[round(max(0, s), 3), round(e, 3)] for s, e in zip(st, en)]


def khoang_ngung(loi, toi_thieu=0.45):
    """Chỗ ngừng nói lấy từ giờ từng chữ: phòng có tiếng nền (quạt, điều hoà) thì máy dò lặng theo độ ồn bỏ sót."""
    return [[round(e + 0.05, 3), round(s - 0.05, 3)] for (_, e, _), (s, _, _) in zip(loi, loi[1:]) if s - e >= toi_thieu]


def gop_lang(ds):
    out = []
    for s, e in sorted(ds):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def doi_canh(path, nguong=0.3):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-vf', f"select='gt(scene,{nguong})',showinfo",
                          '-an', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    return [round(float(x), 2) for x in re.findall(r'pts_time:([\d.]+)', err)]


def anh_luoi(path, dai, ra, so_o=12):
    """Ảnh lưới 4 cột: mỗi ô là 1 khung hình rải đều theo thời gian, ghi giây ở góc."""
    so_o = max(4, min(so_o, int(dai) + 1))
    cot = 4
    hang = (so_o + cot - 1) // cot
    tw = 270
    font = ImageFont.truetype(tim_font(), 26)
    o = []
    for i in range(so_o):
        t = dai * (i + 0.5) / so_o
        tmp = f'{ra}.o{i}.jpg'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.2f}', '-i', path, '-frames:v', '1', '-vf', f'scale={tw}:-2', tmp])
        im = Image.open(tmp).convert('RGB')
        os.remove(tmp)
        ImageDraw.Draw(im).text((8, 6), f'{t:.1f}s', font=font, fill=(255, 230, 0), stroke_width=3, stroke_fill=(0, 0, 0))
        o.append(im)
    th = max(im.height for im in o)
    luoi = Image.new('RGB', (cot * tw, hang * th), (20, 20, 20))
    for i, im in enumerate(o):
        luoi.paste(im, ((i % cot) * tw, (i // cot) * th))
    luoi.save(ra, quality=85)


def nghe(path, model, loc_bia=True):
    """Chuyển lời nói thành chữ, có giờ từng chữ. Cần: kiem_tra.py --cai faster-whisper (lần đầu tự tải model ~1,5 GB)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        log('  Chưa có faster-whisper → bỏ qua phụ đề. Cài: python3 scripts/kiem_tra.py --cai faster-whisper')
        return None
    import numpy as np
    # tự giải mã tiếng bằng ffmpeg (16 kHz, 1 kênh) thay vì để faster-whisper dùng thư viện av: av 19 làm faster-whisper 1.2.1 lỗi
    tieng = np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], nhi_phan=True).stdout, np.float32)
    m = WhisperModel(model, device='auto', compute_type='int8')
    segs, _ = m.transcribe(tieng, language='vi', word_timestamps=True, vad_filter=True)
    ra, het, bao, dai = [], [], 60, len(tieng) / 16000   # het: mọi chữ kể cả câu bị bỏ, để tính chỗ ngừng nói
    for s in segs:
        if s.end >= bao:   # video dài nghe mất nhiều phút: báo tiến độ để người dùng không tưởng máy treo
            log(f'  Đã nghe {int(s.end)}/{int(dai)} giây')
            bao = s.end + 60
        chu = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for w in (s.words or []) if w.word.strip()]
        het += chu
        if loc_bia and (CAU_BIA.search(s.text) or (CAU_KET.search(s.text) and len(s.text.split()) <= 10)):   # chỗ chỉ có tiếng ồn, máy hay "nghe" ra câu kết video YouTube (độ tin cậy vẫn cao)
            log(f'  Bỏ khỏi phụ đề câu nghi máy nghe bịa ở giây {s.start:.1f}: "{s.text.strip()}" (người nói thật có nói thì chạy lại với --khong-loc-bia)')
            continue
        ra += chu
    return ra, het


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dau_vao', nargs='+')
    ap.add_argument('--ra', required=True)
    ap.add_argument('--khong-nghe', action='store_true', help='không chuyển lời thành chữ (video không có lời)')
    ap.add_argument('--khong-loc-bia', action='store_true', help='giữ cả câu kiểu "đăng ký kênh", "cảm ơn các bạn đã xem" (người nói thật có nói)')
    ap.add_argument('--model', default='large-v3-turbo')
    a = ap.parse_args()
    files = []
    for p in a.dau_vao:
        files += sorted(f for f in glob.glob(os.path.join(p, '*')) if f.lower().endswith(DUOI)) if os.path.isdir(p) else [p]
    od = os.path.join(a.ra, 'phan-tich')
    os.makedirs(od, exist_ok=True)
    for f in files:
        ten = os.path.splitext(os.path.basename(f))[0]
        tt = thong_tin(f)
        log(f'Xem {ten}: {tt["dai"]:.1f}s {tt["rong"]}x{tt["cao"]}')
        kq = {'file': os.path.abspath(f), **tt, 'khung': 'doc' if tt['cao'] > tt['rong'] else 'ngang'}
        kq['cho_lang'] = cho_lang(f) if tt['co_tieng'] else []
        kq['ty_le_lang'] = round(sum(e - s for s, e in kq['cho_lang']) / tt['dai'], 2) if tt['co_tieng'] else 1.0
        kq['doi_canh'] = doi_canh(f)
        kq['vung_tieng'] = vung_tieng(f, tt['dai']) if tt['co_tieng'] else []
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tim_mat.py'), f, str(tt['rong']), str(tt['cao']), str(tt['dai'])],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        kq['mat'] = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None
        if kq['mat'] is None and r.returncode == 0:
            log('  Chưa cài OpenCV → phụ đề không tự né mặt. Cài: python3 scripts/kiem_tra.py --cai "opencv-python-headless<5"')
        elif kq['mat'] is None:
            log('  Không dò được mặt → phụ đề không tự né mặt. Lỗi: ' + r.stderr.strip()[-300:])
        if kq['vung_tieng']:
            log(f'  Tiếng đổi giữa chừng ở giây {", ".join(str(int(v[0])) for v in kq["vung_tieng"][1:])} (đổi micro/lọc ồn): dung.py sẽ tự cân')
        kq['loi_noi'], het = None, None
        if tt['co_tieng'] and not a.khong_nghe and kq['ty_le_lang'] < 0.8:
            kq['loi_noi'], het = nghe(f, a.model, not a.khong_loc_bia) or (None, None)
        if kq['loi_noi']:
            kq['van_ban'] = ' '.join(w[2] for w in kq['loi_noi'])
        if het:   # chỗ ngừng tính trên MỌI chữ: câu bỏ khỏi phụ đề không biến thành "chỗ lặng" bị cắt mất
            kq['cho_lang'] = gop_lang(kq['cho_lang'] + khoang_ngung(het))
        anh_luoi(f, tt['dai'], os.path.join(od, ten + '.jpg'))
        ghi_json(os.path.join(od, ten + '.json'), kq)
        print(os.path.join(od, ten + '.json'))


if __name__ == '__main__':
    main()
