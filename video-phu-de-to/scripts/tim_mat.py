# Dò mặt người trong video gốc (OpenCV, chạy trên máy, không tốn tiền) để phụ đề không che mặt, che miệng.
# phan_tich.py gọi tim_mat() → ghi "mat" vào phân tích; dung.py gọi day_mat() để biết cằm nằm đâu trên khung dọc.
import numpy as np
from chung import W, H, run


def tim_mat(path, rong, cao, dai, buoc=1.0):
    """Mỗi `buoc` giây lấy 1 khung, tìm mặt to nhất. Trả về [[giây, x0, y0, x1, y1]] (0–1 theo khung gốc); chưa cài OpenCV thì trả None."""
    try:
        import cv2
    except ImportError:
        return None
    tw = 360
    th = int(round(cao * tw / rong / 2)) * 2
    raw = run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={1 / buoc},scale={tw}:{th}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
              nhi_phan=True).stdout
    loc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    ra = []
    for i in range(len(raw) // (tw * th)):
        k = np.frombuffer(raw, np.uint8, tw * th, i * tw * th).reshape(th, tw)
        mat = loc.detectMultiScale(k, scaleFactor=1.1, minNeighbors=5, minSize=(tw // 8, tw // 8))
        if len(mat):
            x, y, w, h = max(mat, key=lambda m: m[2] * m[3])
            # khung của bộ dò dừng ở môi dưới → cộng thêm 25% chiều cao để tới hết cằm
            ra.append([round(i * buoc + buoc / 2, 2), round(x / tw, 3), round(y / th, 3), round((x + w) / tw, 3), round(min(1, (y + h * 1.25) / th), 3)])
    return ra


def khung_mat(mat, t, rong, cao, khung, z):
    """(đỉnh mặt, đáy cằm) tính bằng pixel trên khung dọc W×H quanh giây t của video gốc, đã tính khớp khung + phóng to.
    Không thấy mặt thì None."""
    gan = [m for m in mat or [] if abs(m[0] - t) <= 1.6]
    if not gan:
        return None
    if khung == 'nen-mo' and abs(rong / cao - W / H) > 0.05:
        s = min(W / rong, H / cao)
        doi = lambda y: y * cao * s + (H - cao * s) / 2
    else:
        s = max(W / rong, H / cao)
        doi = lambda y: y * cao * s - (cao * s - H) / 2
        le = (1 - W / (rong * s)) / 2   # video ngang bị cắt hai bên: bỏ mặt nằm ngoài phần còn thấy
        gan = [m for m in gan if le <= (m[1] + m[3]) / 2 <= 1 - le]
        if not gan:
            return None
    ys = [doi(min(m[2] for m in gan)), doi(max(m[4] for m in gan))]
    if z != 1.0:   # phải khớp công thức phóng to trong dung.py: crop=iw/z:ih/z:...:(ih-oh)*0.35
        ys = [(y - (H - H / z) * 0.35) * z for y in ys]
    return ys


if __name__ == '__main__':   # chạy riêng 1 tiến trình: OpenCV và thư viện av của faster-whisper chung 1 tiến trình thì macOS báo trùng thư viện
    import json, sys
    print(json.dumps(tim_mat(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))))
