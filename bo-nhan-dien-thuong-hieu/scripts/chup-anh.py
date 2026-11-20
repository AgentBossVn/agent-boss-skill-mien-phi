#!/usr/bin/env python3
"""Chụp ấn phẩm HTML thành PNG bằng Chrome / Edge / Brave / Chromium chạy ngầm (headless).

Chạy:  python chup-anh.py <tệp.html | thư-mục> [--ra <thư-mục>]
Kích thước lấy từ <meta name="kho" content="RỘNGxCAO"> của từng tệp.
Thư mục → chụp mọi .html có meta kho; mặc định ra <thư-mục>/xem-truoc/<tên>.png.  Tệp lẻ → mặc định ra cạnh tệp.
Tìm trình duyệt: biến môi trường CHROME, rồi đường chuẩn Mac / Windows / Linux. Không có → báo rõ, thoát mã 1.
"""
import sys, os, re, shutil, subprocess, tempfile, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

KHO_RE = re.compile(r'<meta\s+name="kho"\s+content="(\d+)x(\d+)"', re.I)


def tim_trinh_duyet():
    env = os.environ.get('CHROME')
    if env and Path(env).is_file(): return env
    ung = []
    if sys.platform == 'darwin':
        for ten in ('Google Chrome', 'Microsoft Edge', 'Brave Browser', 'Chromium'):
            ung.append(f'/Applications/{ten}.app/Contents/MacOS/{ten}')
            ung.append(str(Path.home() / f'Applications/{ten}.app/Contents/MacOS/{ten}'))
    elif sys.platform == 'win32':
        goc = [os.environ.get(k) for k in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA')]
        for g in filter(None, goc):
            ung += [rf'{g}\Google\Chrome\Application\chrome.exe', rf'{g}\Microsoft\Edge\Application\msedge.exe',
                    rf'{g}\BraveSoftware\Brave-Browser\Application\brave.exe']
    for p in ung:
        if Path(p).is_file(): return p
    for ten in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'brave-browser'):
        p = shutil.which(ten)
        if p: return p
    return None


def chup(trinh_duyet: str, html: Path, png: Path, w: int, h: int) -> str:
    """Chụp 1 tệp. Trả '' nếu xong, hoặc câu lỗi."""
    png.parent.mkdir(parents=True, exist_ok=True)
    if png.exists(): png.unlink()
    with tempfile.TemporaryDirectory(prefix='chup-anh-') as hs:
        lenh = [trinh_duyet, '--headless=new', f'--screenshot={png.resolve()}', f'--window-size={w},{h}', '--hide-scrollbars',
                '--force-device-scale-factor=1', '--virtual-time-budget=4000', f'--user-data-dir={hs}', '--no-first-run',
                '--disable-gpu', '--default-background-color=FFFFFFFF', html.resolve().as_uri()]
        try: p = subprocess.run(lenh, capture_output=True, timeout=90, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired: return 'trình duyệt chạy quá 90 giây'
    if not png.is_file() or png.stat().st_size < 100:
        return f'trình duyệt không ra ảnh (mã {p.returncode}): ' + p.stderr.decode('utf-8', 'replace')[-300:]
    return ''


def main():
    ap = argparse.ArgumentParser(description='Chụp HTML thành PNG')
    ap.add_argument('nguon'); ap.add_argument('--ra', help='thư mục ra ảnh')
    a = ap.parse_args()
    src = Path(a.nguon).expanduser()
    if not src.exists(): print(f'LỖI: không thấy {src}'); sys.exit(1)
    cac = sorted(src.glob('*.html')) if src.is_dir() else [src]
    ra = Path(a.ra).expanduser() if a.ra else ((src if src.is_dir() else src.parent) / ('xem-truoc' if src.is_dir() else ''))
    trinh = tim_trinh_duyet()
    if not trinh:
        print('LỖI: không thấy Chrome / Edge / Brave / Chromium trên máy. Cài Google Chrome (hoặc đặt biến môi trường CHROME = đường dẫn trình duyệt) rồi chạy lại.')
        sys.exit(1)
    loi, xong = 0, 0
    for f in cac:
        m = KHO_RE.search(f.read_text(encoding='utf-8', errors='replace'))
        if not m:
            if not src.is_dir(): print(f'LỖI: {f.name} thiếu <meta name="kho" content="RỘNGxCAO">'); loi += 1
            continue
        w, h = int(m.group(1)), int(m.group(2)); png = ra / (f.stem + '.png')
        e = chup(trinh, f, png, w, h)
        if e: print(f'✗ {f.name}: {e}'); loi += 1
        else: print(f'✓ {png}  ({w}×{h})'); xong += 1
    if not xong and not loi: print('Không có tệp HTML nào có meta "kho".'); sys.exit(1)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()
