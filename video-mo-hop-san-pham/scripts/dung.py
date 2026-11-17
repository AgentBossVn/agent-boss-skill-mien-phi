# Bước 2: dựng video dọc 9:16 đăng được ngay, theo kế hoạch agent viết + preset của kiểu video.
# Chạy: python3 scripts/dung.py <ke-hoach.json> [--chi-thoi-gian]
#   --chi-thoi-gian: chỉ tính dòng thời gian, in giờ từng cụm phụ đề trên video mới (để đặt chữ/ảnh cho khớp), không dựng.
# Kế hoạch (đường dẫn tương đối tính từ thư mục chứa ke-hoach.json):
# {
#   "dau_ra": "thanh-pham/video.mp4",
#   "doan": [{"file": "clip1.mp4", "tu": 0, "den": 12.5}],            giây trên video gốc, theo thứ tự xuất hiện
#   "chu":  [{"tu": 0, "den": 2.5, "noi_dung": "NỒI CHIÊN 890K", "kieu": "mo_dau"}],   giây trên video MỚI; "den": "het" = tới cuối thân
#   "giong_doc": {"van_ban": "...", "giong": "vi-VN-HoaiMyNeural"} hoặc {"file": "loi.mp3"},   tuỳ chọn
#   "nhac": "nhac.mp3",  "sua_chu": {"chữ sai": "chữ đúng"},  "tu_khoa": ["giảm giá"],  "the_ket": true,
#   "thuong_hieu": "đường/dẫn/thuong-hieu.json"   (bỏ trống = ~/.agent-boss/thuong-hieu.json)
#   "vi_tri_phu_de": 0.75   (tuỳ chọn, 0–1 theo chiều cao: dời phụ đề khi che miệng/mặt)
# }
import asyncio, json, os, re, shutil, sys
from chung import W, H, FPS, ENC, AENC, run, duong_ff, doc_json, ghi_json, thong_tin, preset, thuong_hieu, mau, tim_font, log  # nạp trước: tự đổi sang Python riêng
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from phan_tich import cho_lang
from mau_tieng import bo_can, to_sau_can
from tim_mat import khung_mat

KH_PATH = os.path.abspath(sys.argv[1])
GOC = os.path.dirname(KH_PATH)
KH = doc_json(KH_PATH)
P = preset()
TH = thuong_hieu(KH.get('thuong_hieu') and os.path.join(GOC, KH['thuong_hieu']))
FONT = tim_font(TH.get('font') or P.get('font'))
PD = P.get('phu_de', {})
OUT = os.path.join(GOC, KH.get('dau_ra', 'thanh-pham/video.mp4'))
TMP = os.path.join(os.path.dirname(OUT), '.tam')
os.makedirs(TMP, exist_ok=True)
NHAN, CHINH, CHU = mau(TH['mau_nhan']), mau(TH['mau_chinh']), mau(TH['mau_chu'])


def duong(p):
    return p if os.path.isabs(p) else os.path.join(GOC, p)


def fr(x):
    return round(x * FPS) / FPS


def phan_tich_cua(f):
    """Lấy kết quả phan_tich.py của file này (nếu đã chạy), để dùng lại chỗ lặng + lời nói."""
    ten = os.path.splitext(os.path.basename(f))[0]
    return doc_json(os.path.join(GOC, 'phan-tich', ten + '.json'))


# ---------- 1. dòng thời gian ----------
def cat_lang(f, a, b, lang):
    pad = P.get('dem_cat', 0.08)
    out, cur = [], a
    for s, e in lang:
        s2, e2 = s + pad, e - pad
        if e2 <= cur or s2 >= b or e2 - s2 < 0.1:
            continue
        if s2 > cur:
            out.append((cur, s2))
        cur = max(cur, e2)
    if b > cur:
        out.append((cur, b))
    return [(fr(x), fr(y)) for x, y in out if y - x > 0.1]


def tim_nhip(nhac):
    """Tìm phách nhạc (đơn giản: đỉnh năng lượng âm trầm) -> danh sách giây."""
    import subprocess
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', nhac, '-ac', '1', '-ar', '11025', '-af', 'lowpass=f=200',
                          '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    hop = 512
    e = np.array([np.sum(x[i:i + hop] ** 2) for i in range(0, len(x) - hop, hop)])
    if len(e) < 10:
        return []
    d = np.maximum(0, np.diff(e, prepend=e[0]))
    nguong = d.mean() + d.std()
    nhip, cuoi = [], -1
    for i in range(1, len(d) - 1):
        t = i * hop / 11025
        if d[i] > nguong and d[i] >= d[i - 1] and d[i] >= d[i + 1] and t - cuoi > 0.3:
            nhip.append(round(t, 3))
            cuoi = t
    return nhip


segs, t = [], 0.0   # (file, a, b, ra_a)
SEG_DOAN = []   # khúc thứ i thuộc đoạn nào trong kế hoạch (phụ đề không ghép chữ của hai đoạn khác nhau)
SEG_VUNG = []   # khúc thứ i thuộc vùng tiếng nào (video gốc đổi micro giữa chừng) → (file, số vùng) hoặc None
for so_doan, d in enumerate(KH['doan']):
    f = duong(d['file'])
    tt = thong_tin(f)
    a, b = float(d.get('tu', 0)), min(float(d.get('den', tt['dai'])), tt['dai'])
    pt = phan_tich_cua(f)
    pt = pt if pt.get('file') == os.path.abspath(f) else {}
    if P.get('cat_lang') and tt['co_tieng'] and d.get('cat_lang', True):
        khuc = cat_lang(f, a, b, pt['cho_lang'] if 'cho_lang' in pt else cho_lang(f))
    else:
        khuc = [(fr(a), fr(b))]
    vung = pt.get('vung_tieng') or []
    for x, y in khuc:
        # khúc vắt qua chỗ đổi tiếng thì chẻ đôi, mỗi nửa cân theo vùng của nó
        moc = [x] + [fr(v[0]) for v in vung[1:] if x + 0.3 < v[0] < y - 0.3] + [y]
        for x2, y2 in zip(moc, moc[1:]):
            segs.append([f, x2, y2, t])
            SEG_DOAN.append(so_doan)
            SEG_VUNG.append((f, max(j for j, v in enumerate(vung) if v[0] <= (x2 + y2) / 2)) if vung else None)
            t += y2 - x2

# cân tiếng: các vùng tiếng được dùng kéo về mức trung bình (theo thời lượng) để giọng không đổi đột ngột
CAN = [''] * len(segs)
dung_vung = {}
for (f, x, y, _), v in zip(segs, SEG_VUNG):
    if v:
        dung_vung[v] = dung_vung.get(v, 0) + y - x
if len(dung_vung) > 1 and P.get('giu_tieng_goc', True):
    vg = {v: phan_tich_cua(v[0])['vung_tieng'][v[1]] for v in dung_vung}
    tong = sum(dung_vung.values())
    dich = sum(np.array(vg[v][2]) * s for v, s in dung_vung.items()) / tong
    to = {v: to_sau_can(vg[v][2], vg[v][3], dich) for v in dung_vung}
    to_dich = sum(to[v] * s for v, s in dung_vung.items()) / tong
    CAN = [bo_can(vg[v][2], dich, to_dich - to[v]) if v else '' for v in SEG_VUNG]
    log(f'Cân tiếng {len(dung_vung)} vùng (video gốc đổi micro/lọc ồn giữa chừng)')

NHAC = duong(KH['nhac']) if KH.get('nhac') else (TH.get('nhac') and os.path.expanduser(TH['nhac']))
if NHAC and not os.path.exists(NHAC):
    log(f'Không thấy file nhạc {NHAC} → dựng không nhạc')
    NHAC = None
if P.get('khop_nhip') and NHAC:  # cắt mỗi cảnh đúng vào phách nhạc
    nhip = tim_nhip(NHAC)
    if len(nhip) > 4:
        moi, t = [], 0.0
        ngan, dai_nhat = P.get('canh_ngan_nhat', 0.8), P.get('canh_dai_nhat', 3.5)
        for f, a, b, _ in segs:
            dai = min(b - a, dai_nhat)
            ok = [n - t for n in nhip if ngan <= n - t <= dai]
            if ok:
                dai = ok[-1]   # cảnh kết thúc đúng phách xa nhất còn vừa
            moi.append([f, a, fr(a + dai), t])
            t += fr(a + dai) - a
        segs = moi
THAN = t
END = fr(P.get('the_ket_giay', 2.5)) if KH.get('the_ket', True) and P.get('the_ket_giay', 2.5) > 0 else 0
TONG = THAN + END

# ---------- 2. lời nói -> chữ trên dòng thời gian mới ----------
SUA = {re.sub(r'[^\w]', '', k.lower()): v for k, v in KH.get('sua_chu', {}).items()}


def norm(x):
    return re.sub(r'[^\w]', '', x.lower())


def tts(gd):
    """Giọng đọc AI: edge-tts (miễn phí, cần mạng). Trả về (file mp3, danh sách chữ có giờ)."""
    if gd.get('file'):
        return duong(gd['file']), []
    try:
        import edge_tts
    except ImportError:
        raise SystemExit('Cần giọng đọc AI: python3 scripts/kiem_tra.py --cai edge-tts')
    mp3 = os.path.join(TMP, 'giong-doc.mp3')
    chu = []

    async def go():
        try:
            c = edge_tts.Communicate(gd['van_ban'], gd.get('giong', 'vi-VN-HoaiMyNeural'), rate=gd.get('toc_do', '+8%'),
                                     boundary='WordBoundary')
        except TypeError:  # edge-tts bản cũ
            c = edge_tts.Communicate(gd['van_ban'], gd.get('giong', 'vi-VN-HoaiMyNeural'), rate=gd.get('toc_do', '+8%'))
        with open(mp3, 'wb') as fh:
            async for m in c.stream():
                if m['type'] == 'audio':
                    fh.write(m['data'])
                elif m['type'] == 'WordBoundary':
                    s = m['offset'] / 1e7
                    chu.append([s, s + m['duration'] / 1e7, m['text']])
    asyncio.run(go())
    return mp3, chu


GIONG, TRE_GIONG = None, 0.3
words = []   # [giây mới, chữ, số đoạn trong kế hoạch]
if KH.get('giong_doc'):
    GIONG, wv = tts(KH['giong_doc'])
    words = [[TRE_GIONG + s, tu, 0] for s, e, cum in wv for tu in cum.split()]
elif PD.get('bat', True) and P.get('giu_tieng_goc', True):
    da_lay = set()
    for k, (f, a, b, ra) in enumerate(segs):
        for ws, we, x in (phan_tich_cua(f).get('loi_noi') or []):
            # máy nghe hay ghi giờ đầu chữ sớm hơn thật → chữ bắt đầu trong chỗ lặng đã cắt mà còn ≥ 0,1 giây tiếng trong khúc vẫn giữ
            if (SEG_DOAN[k], ws) not in da_lay and (a - 0.05 <= ws < b or (ws < a and min(we, b) - a >= 0.1)):
                da_lay.add((SEG_DOAN[k], ws))
                words.append([ra + max(0, ws - a), x, SEG_DOAN[k]])
words.sort(key=lambda w: w[0])
# sửa chữ máy nghe sai, khoá được nhiều chữ ("dịch ứng" → "dị ứng"); khoá dài khớp trước
CUM_SUA = sorted(([norm(k) for k in k_.split()], v) for k_, v in KH.get('sua_chu', {}).items() if k_.split())
CUM_SUA.sort(key=lambda kv: -len(kv[0]))
moi, i = [], 0
while i < len(words):
    for ks, v in CUM_SUA:
        if [norm(w[1]) for w in words[i:i + len(ks)]] == ks:
            dau = re.sub(r'^.*?([,.?!]*)$', r'\1', words[i + len(ks) - 1][1])   # giữ dấu câu cuối cụm
            moi += [[words[min(i + j, i + len(ks) - 1)][0], x, words[i][2]] for j, x in enumerate(v.split())]
            if moi and v.split():
                moi[-1][1] += dau
            i += len(ks)
            break
    else:
        moi.append(words[i])
        i += 1
words = moi
for i in range(1, len(words)):
    words[i][0] = max(words[i][0], words[i - 1][0] + 0.12)
# chữ có hoa thường lẫn lộn (OKRs, iPhone) giữ nguyên kiểu viết, không viết hoa toàn bộ
DA_SUA = {norm(x) for v in SUA.values() for x in v.split() if any(c.isupper() for c in x[1:]) and not x.isupper()}
TEN_SUA = {norm(x) for v in SUA.values() for x in v.split() if x[:1].isupper()}   # chữ từ sua_chu (tên riêng) không coi là đầu câu
words = [w for w in words if w[0] < THAN - 0.1]

TU_GHEP = ['các bạn', 'chúng ta', 'mọi người', 'sử dụng', 'quan trọng', 'cực kỳ', 'ví dụ', 'sau đó', 'bây giờ', 'hôm nay',
           'chia sẻ', 'sản phẩm', 'giảm giá', 'miễn phí', 'chất lượng', 'giỏ hàng', 'đặt hàng', 'khách hàng', 'công việc',
           'bắt đầu', 'làm việc', 'tại sao', 'là gì', 'như thế', 'thế nào', 'vì vậy', 'cho nên', 'trở thành', 'nghìn đồng',
           'xã hội', 'nhân viên', 'phát triển', 'năng lực', 'giá trị', 'quản lý']
TU_GHEP += [v.lower() for v in SUA.values() if ' ' in v.strip()]
low = [norm(w[1]) for w in words]
hl, bind = [False] * len(low), [False] * len(low)
for lst, danh_dau in ((KH.get('tu_khoa', []) + P.get('tu_khoa', []), True), (TU_GHEP, False)):
    for p in lst:
        ps = [norm(x) for x in p.split()]
        for i in range(len(low) - len(ps) + 1):
            if low[i:i + len(ps)] == ps:
                for j in range(i, i + len(ps)):
                    hl[j] = hl[j] or danh_dau
                    if j < i + len(ps) - 1:
                        bind[j] = True
for i, w in enumerate(words):   # số tiền, phần trăm luôn nổi bật
    if re.search(r'\d', w[1]):
        hl[i] = True

toi_da = PD.get('toi_da_chu', 4)
# 1) cắt lời thành câu: ngắt ở đầu câu, dấu câu, ngừng > 1 giây, và LUÔN ngắt ở chỗ nối hai đoạn khác nhau của kế hoạch
cau, cur = [], []
for i, (ts, x, k) in enumerate(words):
    viet_tat = sum(ch.isupper() for ch in x) >= 2   # CEO, OKRs, KPI: không coi là đầu câu
    # tên riêng nhiều chữ (Việt Nam) và chữ lấy từ sua_chu (Claude) không coi là đầu câu
    cau_moi = x[:1].isupper() and not viet_tat and norm(x) not in TEN_SUA and not (i > 0 and words[i - 1][1][:1].isupper())
    if cur and (k != words[i - 1][2] or not bind[i - 1] and (cau_moi or ts - words[i - 1][0] > 1.0 or words[i - 1][1][-1] in '?,.!')):
        cau.append(cur)
        cur = []
    cur.append(i)
if cur:
    cau.append(cur)
# 2) chia đều mỗi câu thành cụm ≤ (toi_da - 1) đơn vị (từ ghép tính 1): 4 chữ → 2+2 thay vì 3+1, không để 1 chữ mồ côi
chunks = []
for c in cau:
    dv = []
    for i in c:
        if dv and i > 0 and bind[i - 1] and dv[-1][-1] == i - 1:
            dv[-1].append(i)
        else:
            dv.append([i])
    n = -(-len(dv) // max(1, toi_da - 1))
    j = 0
    for m in range(n):
        co = len(dv) // n + (1 if m < len(dv) % n else 0)
        chunks.append([i for u in dv[j:j + co] for i in u])
        j += co


def hien(x):
    x = x.rstrip(',.') if not x.endswith('?') else x
    return x.upper() if PD.get('in_hoa', True) and norm(x) not in DA_SUA else x


if '--chi-thoi-gian' in sys.argv:
    print(f'Thân video {THAN:.1f}s + thẻ kết {END:.1f}s = {TONG:.1f}s | {len(segs)} khúc')
    for c in chunks:
        print(f'{words[c[0]][0]:6.2f}  ' + ' '.join(hien(words[i][1]) for i in c))
    sys.exit()


# ---------- 3. vẽ chữ ----------
def ve_dong(dr, dong, f, y, vien, mau_vien, bong):
    sp = f.getlength(' ')
    rong = sum(f.getlength(x) for x, _ in dong) + sp * (len(dong) - 1)
    x0 = (W - rong) / 2
    for x, c in dong:
        if bong:
            dr.text((x0 + 4, y + 7), x, font=f, fill=(0, 0, 0, 160), stroke_width=vien, stroke_fill=(0, 0, 0, 160))
        dr.text((x0, y), x, font=f, fill=c, stroke_width=vien, stroke_fill=mau_vien)
        x0 += f.getlength(x) + sp


def chia_dong(toks, f, toi_da_rong):
    """Xuống dòng cho cân: giữ số dòng ít nhất nhưng các dòng dài gần bằng nhau (tránh 1 chữ mồ côi ở dòng cuối)."""
    dong = _tham(toks, f, toi_da_rong)
    if len(dong) > 1:
        sp = f.getlength(' ')
        rong = toi_da_rong
        while rong > 100:
            thu = _tham(toks, f, rong - 20)
            if len(thu) > len(dong):
                break
            rong -= 20
            dong = thu
    return dong


def _tham(toks, f, toi_da_rong):
    sp = f.getlength(' ')
    dong, cur = [], []
    for tk in toks:
        thu = cur + [tk]
        if cur and sum(f.getlength(x) for x, _ in thu) + sp * (len(thu) - 1) > toi_da_rong:
            dong.append(cur)
            cur = [tk]
        else:
            cur = thu
    return dong + [cur] if cur else dong


def ve_khoi(toks, co, y_tam, vien, mau_vien, bong=True, nen=None, xoay=0, mat=None):
    """Vẽ 1 khối chữ (nhiều màu) vào ảnh trong suốt cỡ khung, tự xuống dòng và thu nhỏ cho vừa vùng an toàn.
    mat = (đỉnh mặt, đáy cằm): chữ không được đè lên khoảng này → thử dưới cằm, rồi trên đầu, chật thì thu nhỏ chữ.
    Trả về (ảnh, vị trí: 'giua' | 'duoi' | 'tren' | 'de')."""
    rong_toi_da = W - 2 * P.get('le', 90)
    tren_cung, day = H * 0.09, H * 0.8   # trên 9%: thanh "Đang theo dõi | Dành cho bạn"; dưới 80%: tên kênh, chú thích TikTok
    while True:
        f = ImageFont.truetype(FONT, co)
        dong = chia_dong(toks, f, rong_toi_da)
        lh = int(co * 1.2)
        cao = lh * len(dong)
        if co > 40 and len(dong) > 3:
            co = int(co * 0.88)
            continue
        y0, vt = int(y_tam - cao / 2), 'giua'
        if mat:
            ft, fb = mat
            if not (y0 + cao < ft - 16 or y0 > fb + 16):          # chỗ mặc định đè lên mặt
                if fb + 24 + cao <= day:
                    y0, vt = int(fb + 24), 'duoi'
                elif ft - 24 - cao >= tren_cung:
                    y0, vt = int(ft - 24 - cao), 'tren'
                elif co > 56:
                    co = int(co * 0.9)
                    continue
                else:
                    y0, vt = int(day - cao), 'de'
        break
    y0 = int(min(max(y0, tren_cung), day - cao))
    y_tam = y0 + cao / 2
    lop = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lop)
    if nen:
        sp = f.getlength(' ')
        rong = max(sum(f.getlength(x) for x, _ in d) + sp * (len(d) - 1) for d in dong)
        dr.rounded_rectangle(((W - rong) / 2 - 36, y0 - 22, (W + rong) / 2 + 36, y0 + lh * len(dong) + 14), radius=28, fill=nen)
    for i, d in enumerate(dong):
        ve_dong(dr, d, f, y0 + i * lh, vien, mau_vien, bong and not nen)
    if xoay:
        lop = lop.rotate(xoay, resample=Image.BICUBIC, center=(W / 2, y_tam))
    return lop, vt


os.makedirs(os.path.join(TMP, 'cap'), exist_ok=True)
trong = os.path.join(TMP, 'cap', 'trong.png')
Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(trong)
mau_chu_pd = mau(PD['mau']) if PD.get('mau') else CHU
mau_vien_pd = mau(PD['mau_vien']) if PD.get('mau_vien') else (0, 0, 0, 255)
nen_pd = mau(PD['nen'][:7], int(PD['nen'][7:9] or 'ff', 16)) if PD.get('nen') else None
y_pd = int(H * float(KH.get('vi_tri_phu_de') or PD.get('vi_tri', 0.69)))   # kế hoạch dời được khi phụ đề che mặt
muc = []   # (tên ảnh, giây hiện)

# phóng to / thu nhỏ xen kẽ: tính trước để biết mặt nằm đâu khi đặt phụ đề
khung = P.get('khung', 'cat')
doi = P.get('doi_khung_giay', 0)
ZS, z, moc = [], 1.0, 0.0
for f, a, b, ra in segs:
    if doi and ra - moc >= doi:
        z = P.get('zoom', 1.2) if z == 1.0 else 1.0
        moc = ra
    ZS.append(z)
_TT = {}


def mat_luc(t1, t2):
    """(đỉnh mặt cao nhất, đáy cằm thấp nhất) trong khoảng t1–t2 của video mới; không thấy mặt thì None."""
    if any(float(c['tu']) < t2 and float(c['den']) > t1 for c in KH.get('chen_anh', [])):
        return None   # đang chiếu ảnh minh hoạ phủ kín khung: mặt người nói bị che, phụ đề về chỗ mặc định
    ds = []
    for i, (f, a, b, ra) in enumerate(segs):
        if ra < t2 and ra + (b - a) > t1:
            pt = phan_tich_cua(f)
            mat = pt.get('mat') if pt.get('file') == os.path.abspath(f) else None
            if mat:
                tt = _TT.setdefault(f, thong_tin(f))
                k = khung_mat(mat, a + max(t1, ra) - ra, tt['rong'], tt['cao'], khung, ZS[i])
                if k:
                    ds.append(k)
    return (min(k[0] for k in ds), max(k[1] for k in ds)) if ds else None


def chu_tren_luc(t1, t2):
    """Có chữ đặt sẵn ở nửa trên khung (câu mở đầu, tiêu đề) đang hiện trong t1–t2 không."""
    return any(float(c.get('tu', 0)) < t2 and (THAN if c.get('den', 'het') == 'het' else float(c['den'])) > t1
               and P.get('chu', {}).get(c.get('kieu', 'nhan'), {}).get('vi_tri', 0.2) < 0.45 for c in KH.get('chu', []))


def them(ten, du):
    if du > 0.001:
        muc.append((ten, du))


truoc = 0.0
for k, c in enumerate(chunks):
    bd = words[c[0]][0]
    sau = words[chunks[k + 1][0]][0] if k + 1 < len(chunks) else THAN
    kt = min(sau, bd + 2.4, THAN)
    if kt - bd < 0.05:
        continue
    them('trong.png', bd - truoc)
    to = any(hl[i] for i in c) and PD.get('co_to') and len(c) <= 2
    co = PD.get('co_to', 118) if to else PD.get('co', 84)
    if PD.get('kieu') == 'karaoke':   # tô màu từng chữ đang đọc
        for j, i in enumerate(c):
            t1 = bd if j == 0 else words[i][0]
            t2 = words[c[j + 1]][0] if j + 1 < len(c) else kt
            toks = [(hien(words[m][1]), NHAN if m == i else mau_chu_pd) for m in c]
            p = f'k{k:03d}_{j}.png'
            lop, vt = ve_khoi(toks, co, y_pd, PD.get('vien', 8), mau_vien_pd, PD.get('bong', True), nen_pd, mat=mat_luc(t1, t2))
            if vt == 'tren' and chu_tren_luc(t1, t2):   # lên trên đầu mà đang có câu mở đầu ở đó → nhường câu mở đầu
                p = 'trong.png'
            else:
                lop.save(os.path.join(TMP, 'cap', p))
            them(p, t2 - t1)
    else:
        toks = [(hien(words[i][1]), NHAN if (hl[i] or to) else mau_chu_pd) for i in c]
        p = f'c{k:03d}.png'
        lop, vt = ve_khoi(toks, co, y_pd, PD.get('vien', 9), mau_vien_pd, PD.get('bong', True), nen_pd,
                          xoay=3 if to and PD.get('nghieng_chu_to', True) else 0, mat=mat_luc(bd, kt))
        if vt == 'tren' and chu_tren_luc(bd, kt):   # lên trên đầu mà đang có câu mở đầu ở đó → nhường câu mở đầu
            p = 'trong.png'
        else:
            lop.save(os.path.join(TMP, 'cap', p))
        them(p, kt - bd)
    truoc = kt
them('trong.png', TONG - truoc + 1)
with open(os.path.join(TMP, 'cap', 'list.txt'), 'w', encoding='utf-8') as fh:
    fh.write('ffconcat version 1.0\n')
    for p, du in muc:
        fh.write(f"file '{p}'\nduration {du:.3f}\n")
    fh.write("file 'trong.png'\n")

# chữ đặt sẵn (tiêu đề mở đầu, giá, lời kêu gọi...)
lop_chu = []
for k, c in enumerate(KH.get('chu', [])):
    kieu = P.get('chu', {}).get(c.get('kieu', 'nhan'), {})
    bd = float(c.get('tu', 0))
    kt = THAN if c.get('den', 'het') == 'het' else min(float(c['den']), THAN)
    nen = {'nhan': NHAN, 'chinh': CHINH}.get(kieu.get('nen')) if kieu.get('nen') else None
    mc = {'nhan': NHAN, 'chinh': CHINH}.get(kieu.get('mau'), CHU)
    toks = [(x, mc) for x in c['noi_dung'].split()]
    p = os.path.join(TMP, f'chu{k}.png')
    ve_khoi(toks, kieu.get('co', 92), int(H * kieu.get('vi_tri', 0.2)), kieu.get('vien', 0 if nen else 8), (0, 0, 0, 255),
            nen=nen, xoay=kieu.get('xoay', 0))[0].save(p)
    lop_chu.append((p, bd, kt))

# ---------- 4. dựng từng khúc hình ----------
os.makedirs(os.path.join(TMP, 'khuc'), exist_ok=True)
ds = []
for i, (f, a, b, ra) in enumerate(segs):
    tt = thong_tin(f)
    z = ZS[i]
    zoom = f',crop=iw/{z}:ih/{z}:(iw-ow)/2:(ih-oh)*0.35,scale={W}:{H}' if z != 1.0 else ''
    if khung == 'nen-mo' and abs(tt['rong'] / tt['cao'] - W / H) > 0.05:
        vf = (f'[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:4,eq=brightness=-0.1[bg];'
              f'[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2{zoom},setsar=1,fps={FPS}[v]')
    else:
        vf = f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}{zoom},setsar=1,fps={FPS}[v]'
    n = max(1, round((b - a) * FPS))
    dur = n / FPS
    if tt['co_tieng'] and P.get('giu_tieng_goc', True):
        af = f';[0:a]aresample=48000,{CAN[i]}afade=t=in:d=0.015,afade=t=out:st={max(0, dur - 0.015):.3f}:d=0.015[a]'
        vao = ['-ss', f'{a:.3f}', '-t', f'{dur:.3f}', '-i', f]
    else:
        af = ';[1:a]anull[a]'
        vao = ['-ss', f'{a:.3f}', '-t', f'{dur:.3f}', '-i', f, '-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
    p = os.path.join(TMP, 'khuc', f'k{i:03d}.mp4')
    run(['ffmpeg', '-y', '-v', 'error'] + vao + ['-filter_complex', vf + af, '-map', '[v]', '-map', '[a]',
                                              '-frames:v', str(n)] + ENC + AENC + ['-t', f'{dur:.3f}', p])
    ds.append(p)

if END:   # thẻ kết từ hồ sơ thương hiệu
    the = Image.new('RGBA', (W, H), CHINH)
    y = int(H * 0.30)
    if TH.get('logo') and os.path.exists(os.path.expanduser(TH['logo'])):
        lg = Image.open(os.path.expanduser(TH['logo'])).convert('RGBA')
        lg.thumbnail((520, 520))
        the.alpha_composite(lg, ((W - lg.width) // 2, y - lg.height // 2))
        y += lg.height // 2 + 140
    if TH.get('ten'):
        the.alpha_composite(ve_khoi([(x, CHU) for x in TH['ten'].split()], 96, y, 0, (0, 0, 0, 255), bong=False)[0])
        y += 230
    the.alpha_composite(ve_khoi([(x, CHINH) for x in TH['cau_ket'].upper().split()], 64, y, 0, (0, 0, 0, 255), nen=NHAN)[0])
    pthe = os.path.join(TMP, 'the-ket.png')
    the.convert('RGB').save(pthe)
    n = round(END * FPS)
    p = os.path.join(TMP, 'khuc', 'the-ket.mp4')
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', pthe, '-f', 'lavfi', '-t', f'{END:.3f}', '-i', 'anullsrc=r=48000:cl=stereo',
         '-filter_complex', f"[0:v]scale=2160:3840,zoompan=z='1+0.03*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
         f"fade=t=in:st=0:d=0.3,setsar=1[v]", '-map', '[v]', '-map', '1:a', '-frames:v', str(n)] + ENC + AENC + ['-t', f'{END:.3f}', p])
    ds.append(p)
with open(os.path.join(TMP, 'khuc', 'list.txt'), 'w', encoding='utf-8') as fh:
    fh.writelines(f"file '{duong_ff(x)}'\n" for x in ds)
nen_vid = os.path.join(TMP, 'nen.mp4')
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(TMP, 'khuc', 'list.txt'), '-c', 'copy', nen_vid])

# ---------- 5. ghép chữ + tiếng ----------
vao = ['-i', nen_vid, '-f', 'concat', '-safe', '0', '-i', os.path.join(TMP, 'cap', 'list.txt')]
fc = [f'[1:v]fps={FPS},format=rgba[cap]']
truoc_v = '[0:v]'
# ảnh minh hoạ chèn xen (nằm dưới chữ đặt sẵn và phụ đề): tiếng vẫn chạy, hình cắt sang ảnh, ảnh luôn chuyển động
ANH = [c for c in KH.get('chen_anh', []) if float(c['tu']) < THAN]
for j, c in enumerate(ANH):
    bd = float(c['tu'])
    du = min(float(c['den']), THAN) - bd
    n = max(1, round(du * FPS))
    cd = c.get('chuyen_dong') or ('zoom_in', 'zoom_out', 'lia')[j % 3]
    zz = {'zoom_out': f'1.15-0.15*on/{n}', 'lia': '1.15'}.get(cd, f'1+0.15*on/{n}')
    xx = f'(iw-iw/zoom)*on/{n}' if cd == 'lia' else 'iw/2-(iw/zoom/2)'
    fc.append(f"[{2 + len(lop_chu) + j}:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
              f"zoompan=z='{zz}':x='{xx}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},setsar=1,setpts=PTS-STARTPTS+{bd:.3f}/TB[anh{j}]")
    fc.append(f'{truoc_v}[anh{j}]overlay=0:0:eof_action=pass[va{j}]')
    truoc_v = f'[va{j}]'
for k, (p, bd, kt) in enumerate(lop_chu):
    vao += ['-loop', '1', '-t', f'{TONG:.3f}', '-i', p]
    fc.append(f"{truoc_v}[{2 + k}:v]overlay=0:0:enable='between(t,{bd:.3f},{kt - 0.02:.3f})'[v{k}]")
    truoc_v = f'[v{k}]'
for c in ANH:
    du = min(float(c['den']), THAN) - float(c['tu'])
    vao += ['-loop', '1', '-framerate', str(FPS), '-t', f'{du:.3f}', '-i', duong(c['anh'])]
fc.append(f'{truoc_v}[cap]overlay=0:0:eof_action=pass,format=yuv420p[vout]')
idx = 2 + len(lop_chu) + len(ANH)
co_loi = bool(words) or bool(GIONG)
tieng = []
if P.get('giu_tieng_goc', True):
    fc.append('[0:a]highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=9' + ('' if co_loi else ',volume=0.6') + '[goc]')
    tieng.append('[goc]')
if GIONG:
    vao += ['-i', GIONG]
    ms = int(TRE_GIONG * 1000)
    fc.append(f'[{idx}:a]adelay={ms}|{ms},aresample=48000,loudnorm=I=-14:TP=-1.5[giong]')
    tieng.append('[giong]')
    idx += 1
if NHAC:
    vao += ['-stream_loop', '-1', '-i', NHAC]
    al = P.get('nhac', {}).get('am_luong' if co_loi else 'khi_khong_loi', 0.18 if co_loi else 0.7)
    fc.append(f'[{idx}:a]atrim=duration={TONG:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,'
              f'loudnorm=I=-14:TP=-2,volume={al},afade=t=out:st={max(0, TONG - 1.2):.3f}:d=1.2[nhac]')
    tieng.append('[nhac]')
if tieng:
    fc.append(''.join(tieng) + f'amix=inputs={len(tieng)}:normalize=0:duration=longest,atrim=duration={TONG:.3f},alimiter=limit=0.95[aout]')
else:
    fc.append('[0:a]anull[aout]')
with open(os.path.join(TMP, 'filter.txt'), 'w', encoding='utf-8') as fh:   # chỉ để xem lại khi gỡ lỗi
    fh.write(';\n'.join(fc))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
run(['ffmpeg', '-y', '-v', 'error'] + vao + ['-filter_complex', ';'.join(fc), '-map', '[vout]',
                                          '-map', '[aout]', '-frames:v', str(round(TONG * FPS)), '-c:v', 'libx264', '-preset', 'medium',
                                          '-crf', '19', '-r', str(FPS), '-pix_fmt', 'yuv420p'] + AENC + ['-movflags', '+faststart', OUT])

# ảnh bìa: khung hình giữa câu mở đầu (đã có chữ)
md = next((c for c in KH.get('chu', []) if c.get('kieu') == 'mo_dau'), None)
t_bia = min(THAN - 0.1, (float(md['tu']) + 0.8) if md else 1.0)
bia = os.path.splitext(OUT)[0] + '-bia.jpg'
run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t_bia:.2f}', '-i', OUT, '-frames:v', '1', '-q:v', '2', bia])
if '--giu-tam' not in sys.argv:
    shutil.rmtree(TMP, ignore_errors=True)
print(json.dumps({'video': OUT, 'bia': bia, 'dai_giay': round(TONG, 1), 'so_khuc': len(segs), 'so_cum_phu_de': len(chunks),
                  'nhac': bool(NHAC), 'giong_doc': bool(GIONG)}, ensure_ascii=False))
