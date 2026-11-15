# Tính 4 góc tứ giác bao 1 chi tiết dài hình viên thuốc (ô đèn, khe, tay nắm…) từ 2 đầu mút + nửa bề ngang.
# Chạy: python khung-vien-thuoc.py xt,yt xb,yb nua_ngang [thu_vao=0]   → in "TL TR BR BL" để đưa vào dan-chi-tiet-that.py
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import sys
import numpy as np

if len(sys.argv) < 4:
    sys.exit('Cách chạy: python khung-vien-thuoc.py xt,yt xb,yb nua_ngang [thu_vao=0]')
t = np.array(list(map(float, sys.argv[1].split(',')))); b = np.array(list(map(float, sys.argv[2].split(','))))
h = float(sys.argv[3]); s = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
u = (b - t) / np.linalg.norm(b - t); w = np.array([-u[1], u[0]]); w = w if w[0] > 0 else -w
t = t + s * u; b = b - s * u; h = h - s
print(' '.join('%.1f,%.1f' % tuple(p) for p in (t - h * w, t + h * w, b + h * w, b - h * w)))
