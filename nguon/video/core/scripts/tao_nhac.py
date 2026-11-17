# Tự tạo nhạc nền lo-fi nhẹ (piano điện + bass + trống khẽ) bằng code: không bản quyền, không cần mạng, không tốn tiền.
# dung.py gọi khi kế hoạch và hồ sơ thương hiệu đều không có nhạc. Mỗi "hat" (thường là tên video) ra hợp âm, giọng, nhịp khác nhau.
# Chạy riêng: python3 scripts/tao_nhac.py <giây> <ra.wav> [hạt]
import random, sys
import numpy as np
from chung import run

SR = 44100
# vòng hợp âm (bậc trong giọng trưởng, nửa cung tính từ chủ âm), nghe ấm và trung tính, hợp nền giọng nói
VONG = [[0, 9, 5, 7], [0, 7, 9, 5], [9, 5, 0, 7], [0, 4, 9, 5], [5, 7, 0, 9]]
THU = {0: (0, 4, 7, 11), 4: (0, 3, 7, 10), 5: (0, 4, 7, 11), 7: (0, 4, 7, 10), 9: (0, 3, 7, 10)}  # maj7 / m7 / dominant 7


def hz(n):
    return 440 * 2 ** ((n - 69) / 12)


def piano(f, dai):
    t = np.arange(int(SR * dai)) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.8 for k in (1, 2, 3, 4))
    return s * np.exp(-t * 1.6) * np.minimum(1, t / 0.01)


def tao_nhac(giay, ra, hat='agent-boss'):
    r = random.Random(hat)
    bpm = r.choice([80, 84, 88, 92])
    chu = r.choice([57, 58, 60, 62, 63])          # chủ âm (A3–Eb4)
    vong = r.choice(VONG)
    phach = 60 / bpm
    o = phach * 4                                   # 1 ô nhịp = 4 phách, mỗi hợp âm 1 ô
    n = int(SR * (giay + o))
    L = np.zeros(n)
    so_o = int(giay / o) + 1
    for i in range(so_o):
        goc = chu + vong[i % 4]
        bd = int(i * o * SR)
        for j, q in enumerate(THU[vong[i % 4]]):    # rải hợp âm nhẹ
            s = piano(hz(goc + q), o * 1.2) * 0.16
            k = bd + int(j * 0.02 * SR)
            L[k:k + len(s)] += s[:n - k]
        if r.random() < 0.7:                        # nốt nhắc lại ở phách 3
            s = piano(hz(goc + 12 + THU[vong[i % 4]][r.randrange(4)]), o * 0.6) * 0.07
            k = bd + int(2 * phach * SR)
            L[k:k + len(s)] += s[:n - k]
        t = np.arange(int(SR * o)) / SR             # bass
        b = np.sin(2 * np.pi * hz(goc - 24) * t) * np.minimum(1, t / 0.02) * np.exp(-t * 0.8) * 0.28
        L[bd:bd + len(b)] += b[:n - bd]
        for p in range(4):                          # trống khẽ: kick phách 1, 3; hat mỗi nửa phách
            k = bd + int(p * phach * SR)
            if p in (0, 2):
                t = np.arange(int(SR * 0.25)) / SR
                s = np.sin(2 * np.pi * (50 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14) * 0.35
                L[k:k + len(s)] += s[:n - k]
            for h in (0, 0.5):
                kh = k + int(h * phach * SR)
                s = np.random.default_rng(i * 8 + p * 2 + int(h * 2)).standard_normal(int(SR * 0.04)) * np.exp(-np.arange(int(SR * 0.04)) / SR * 90) * (0.03 if h else 0.045)
                L[kh:kh + len(s)] += s[:n - kh]
    L = L[:int(SR * giay)]
    L = (L / (np.abs(L).max() + 1e-9) * 0.8).astype(np.float32)
    # ffmpeg: làm ấm (cắt bớt tiếng cao), thêm vang, ra 2 kênh
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
         'lowpass=f=5000,aecho=0.8:0.6:60|120:0.25|0.15,aformat=channel_layouts=stereo,'
         'afade=t=in:d=0.5', ra], du_lieu=L.tobytes())
    return ra


if __name__ == '__main__':
    print(tao_nhac(float(sys.argv[1]), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'agent-boss'))
