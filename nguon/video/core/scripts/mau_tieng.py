# "Màu tiếng" của video gốc: phát hiện chỗ điện thoại đổi micro / bật lọc ồn giữa chừng (giọng đang ồm bỗng mỏng, to hẳn lên)
# và tạo bộ cân tiếng để các vùng nghe gần giống nhau khi ghép.
# phan_tich.py gọi vung_tieng() → ghi "vung_tieng" vào phân tích; dung.py gọi bo_can() để cân từng khúc.
import numpy as np
from chung import run

SR = 16000
DAI = [(80, 300), (300, 600), (600, 1200), (1200, 2500), (2500, 5000), (5000, 8000)]
TAM = [190, 450, 900, 1800, 3600, 6500]
NGUONG_DB = 8      # hai vùng chênh độ sáng tiếng từ 8 dB trở lên mới coi là đổi tiếng (giọng nói bình thường chênh 2–4 dB)
NGUONG_NOI_DB = 20  # giây nhỏ hơn mức nói to nhất 20 dB trở xuống = lặng hoặc ồn nền, không đo
TRAN_DB = 12       # cân tối đa ±12 dB mỗi dải: tiếng cao đã mất hẳn thì đẩy quá tay chỉ ra tiếng xì


def doc_tieng(path):
    return np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             nhi_phan=True).stdout, np.float32)


def nang_luong(c):
    """Năng lượng 6 dải tần của một đoạn tiếng."""
    sp = np.abs(np.fft.rfft(c * np.hanning(len(c)))) ** 2
    f = np.fft.rfftfreq(len(c), 1 / SR)
    return np.array([sp[(f >= a) & (f < b)].sum() + 1e-12 for a, b in DAI])


def do_sang(e):
    return 10 * np.log10(e[3:].sum() / e[:3].sum())


def _chia(sang, dau, cuoi, it_nhat=3):
    """Tìm 1 điểm chia làm 2 phía chênh độ sáng nhiều nhất; đủ ngưỡng thì chia tiếp từng phía."""
    best, s_best = 0, None
    for s in range(dau + it_nhat, cuoi - it_nhat + 1):
        d = abs(np.mean(sang[dau:s]) - np.mean(sang[s:cuoi]))
        if d > best:
            best, s_best = d, s
    if s_best is None or best < NGUONG_DB:
        return []
    return _chia(sang, dau, s_best) + [s_best] + _chia(sang, s_best, cuoi)


def vung_tieng(path, dai):
    """Trả về [] nếu tiếng đều; có chỗ đổi tiếng thì trả các vùng [từ giây, đến giây, mức 6 dải (dB so với tổng), độ to (dB)].
    Chỉ đo các giây có tiếng nói: giây lặng hay chỉ có tiếng ồn nền mà tính vào thì máy tưởng là một vùng tiếng khác."""
    x = doc_tieng(path)
    n = SR   # cửa sổ 1 giây
    e = [nang_luong(x[i:i + n]) for i in range(0, len(x) - n + 1, n)]
    to = np.array([10 * np.log10(np.mean(x[i:i + n] ** 2) + 1e-12) for i in range(0, len(x) - n + 1, n)])
    if len(e) < 8:
        return []
    noi = [i for i in range(len(e)) if to[i] >= np.percentile(to, 90) - NGUONG_NOI_DB]
    if len(noi) < 8:
        return []
    sang = np.array([do_sang(e[i]) for i in noi])
    moc = _chia(sang, 0, len(noi))
    if not moc:
        return []
    bien = [0] + moc + [len(noi)]
    vung = []
    for k, (a, b) in enumerate(zip(bien, bien[1:])):
        cs = noi[a:b]
        tong = np.sum([e[i] for i in cs], axis=0)
        to_v = 10 * np.log10(np.mean([10 ** (to[i] / 10) for i in cs]))
        vung.append([0.0 if k == 0 else float(noi[a]), float(dai) if b == len(noi) else float(noi[b]),
                     [round(float(10 * np.log10(v / tong.sum())), 1) for v in tong], round(float(to_v), 1)])
    return vung


def tang_giam(muc, dich):
    return [max(-TRAN_DB, min(TRAN_DB, d - m)) for m, d in zip(muc, dich)]


def to_sau_can(muc, to, dich):
    """Độ to (dB) của vùng sau khi cân dải tần: cân xong mới biết cần tăng/giảm bao nhiêu cho bằng các vùng khác."""
    return to + 10 * np.log10(sum(10 ** ((m + g) / 10) for m, g in zip(muc, tang_giam(muc, dich))))


def bo_can(muc, dich, tang_db=0.0):
    """Bộ lọc ffmpeg đưa vùng có mức 'muc' về gần 'dich' (mỗi dải tối đa ±TRAN_DB), rồi tăng/giảm tang_db cho bằng độ to."""
    g = tang_giam(muc, dich)
    diem = [(0, g[0])] + list(zip(TAM, g)) + [(20000, g[-1])]
    return ("firequalizer=gain_entry='" + ';'.join(f'entry({f},{x:.1f})' for f, x in diem) + "',"
            + f'volume={max(-8.0, min(8.0, tang_db)):.1f}dB,')
