# Đặt chữ + logo thật lên ảnh cảnh AI vẽ (AI KHÔNG vẽ chữ). Dựng trang HTML rồi chụp bằng Chrome chạy ngầm.
# Chạy: python dat-chu.py cau-hinh.json [ten-anh ...]     → ảnh ra ở <thư mục cấu hình>/ra/<ten-anh>.png
# Mẫu cấu hình: ../references/mau-dat-chu.json. Đường dẫn ảnh trong cấu hình tính từ thư mục chứa tệp cấu hình.
# Kiểu dòng chữ: lon (chữ to màu thương hiệu) · lon-trang (chữ to trắng viền màu) · dai (dải màu) · dai-toi (dải tối) · nho
# Khoá mỗi ảnh: "kieu_chu" = nghieng-dam (mặc định: nghiêng, đậm, viền trắng, CHỮ HOA) · dam (đứng, đậm 800, không viền,
#   chữ thường như câu, bóng nhẹ — gia dụng/thực phẩm) · thanh-lich (chữ có chân Playfair Display, đứng, không hoa toàn bộ
#   — mỹ phẩm/sách/thời trang) · "nen_toi": true = chữ "nho" trắng + bóng tối (dùng khi nền ảnh tối)
#   · phang (phẳng, hiện đại, không viền: "lon" màu chữ chính, "lon-trang" màu nhấn ("mau_nhan" trên nền tối, "mau" trên nền sáng) — hợp cảnh dựng bằng code và nền màu đặc)
# Thêm 2 kiểu dòng cho ảnh có nhiều khoảng trống (cảnh dựng bằng code, cảnh ghép): y (1 ý lợi ích có dấu tích tròn) · nut (nút kêu gọi bo tròn).
#   "mau_nhan" = màu thứ hai của bao bì (mặc định = mau): dùng cho dấu tích, nút, chữ nhấn của kiểu phang.
# Ra: <tên>.png + <tên>.jpg (chất lượng 92, cần Pillow; thiếu Pillow thì chỉ có PNG).
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import html, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

def tim_chrome():  # Chrome trước, không có thì Edge (Windows luôn có Edge; cùng nền Chromium, cùng cờ headless)
    if os.environ.get('CHROME'): return os.environ['CHROME']
    pf = [os.environ.get(k, '') for k in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA')]
    cho = (['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
           + [os.path.join(d, r) for r in (r'Google\Chrome\Application\chrome.exe', r'Microsoft\Edge\Application\msedge.exe') for d in pf if d])
    for p in cho:
        if os.path.exists(p): return p
    for n in ('google-chrome', 'chromium', 'chromium-browser', 'chrome', 'msedge', 'microsoft-edge'):
        if shutil.which(n): return shutil.which(n)
    sys.exit('Không thấy Chrome hay Edge. Cài Google Chrome hoặc đặt biến CHROME trỏ tới tệp chạy Chrome/Edge.')

def chup(chrome, hp, png, W, H):
    """Chụp trang HTML thành PNG đúng W×H bằng Chrome/Edge chạy ngầm. Trả '' khi xong, hoặc dòng lỗi. (dung-canh-bang-code.py dùng chung)"""
    if os.path.exists(png): os.remove(png)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as ho:  # hồ sơ riêng: không đụng trình duyệt đang mở của người dùng (Edge/Chrome đang chạy sẽ nuốt lệnh)
        try:
            r = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                                '--allow-file-access-from-files', f'--user-data-dir={ho}', '--no-first-run', '--use-mock-keychain', '--password-store=basic', f'--window-size={W},{H}',
                                '--virtual-time-budget=8000', f'--screenshot={png}', Path(hp).as_uri()], capture_output=True, timeout=180)
            loi = r.stderr.decode('utf-8', 'ignore')[-300:]
        except subprocess.TimeoutExpired:
            loi = 'quá 180 giây chưa xong (Chrome treo)'
    # Chrome đôi khi thoát mã lỗi (watchdog) dù đã chụp xong → chỉ coi là hỏng khi không có tệp PNG
    return '' if os.path.exists(png) and os.path.getsize(png) > 0 else (loi or 'không ra tệp PNG')

def uri(goc, p):
    p = p if os.path.isabs(p) else os.path.join(goc, p)
    if not os.path.exists(p): sys.exit(f'Không thấy tệp: {p}')
    return Path(os.path.abspath(p)).as_uri()  # Windows: file:///C:/… (đúng chuẩn)

# CSS riêng từng kiểu chữ (nghieng-dam = kiểu gốc, không cần ghi đè). Đặt SAU css gốc nên thắng.
KIEU_CHU = {
    'nghieng-dam': '',
    'dam': '''.h{font-style:normal;font-weight:800;text-transform:none;line-height:1.15}
.h::before{-webkit-text-stroke:0;color:transparent;filter:none}
.h span{color:var(--m);background-image:none;-webkit-background-clip:border-box;background-clip:border-box;-webkit-text-fill-color:var(--m);
  text-shadow:0 .04em .12em rgba(15,25,45,.35)}
.lon-trang::before{color:var(--m);-webkit-text-stroke:.1em var(--m);filter:drop-shadow(0 .05em .1em rgba(15,25,45,.35))}
.lon-trang span{color:#fff;-webkit-text-fill-color:#fff}
.bang{transform:none}.bang b{text-transform:none}''',
    'thanh-lich': '''.h{font-family:'Playfair Display','Be Vietnam Pro',Georgia,serif;font-style:normal;font-weight:700;text-transform:none;line-height:1.15;font-variant-numeric:lining-nums}
.h::before{-webkit-text-stroke:.05em #fff;filter:drop-shadow(0 .05em .14em rgba(15,25,45,.3))}
.lon-trang::before{color:var(--m);-webkit-text-stroke:.09em var(--m)}
.bang{transform:none}.bang b{font-family:'Playfair Display','Be Vietnam Pro',Georgia,serif;font-weight:600;text-transform:none;font-variant-numeric:lining-nums}''',
    'phang': '''.h{font-style:normal;font-weight:900;text-transform:none;line-height:1.1;letter-spacing:-.012em;padding:.04em 0 0}
.h::before{content:none}
.h span{background-image:none;color:var(--c);-webkit-text-fill-color:var(--c)}
.lon-trang span{color:var(--nc);-webkit-text-fill-color:var(--nc)}
.khoi::before{content:none}
.bang{transform:none;margin:0 0 .35em 0}.bang i{display:none}
.bang b{border-radius:999px;text-transform:none;letter-spacing:.01em;background:var(--n);color:var(--tn);box-shadow:none;padding:.3em .8em .34em}
.dai-toi b{background:var(--t);color:#fff}''',
}

def dong(d):
    k, t = d.get('kieu', 'lon'), html.escape(d['chu']); s = d.get('co', {'y': .42, 'nut': .44}.get(k, 1))
    if k in ('lon', 'lon-trang'):
        return f'<div class="h {k}" style="font-size:{s}em" data-t="{t}"><span>{t}</span></div>'
    if k in ('dai', 'dai-toi'):
        return f'<div class="bang {k}" style="font-size:{s}em"><i></i><i></i><i></i><b>{t}</b></div>'
    if k == 'y':
        return (f'<div class="y" style="font-size:{s}em"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12"/>'
                f'<path d="M6.5 12.5l3.6 3.6 7.4-7.8" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>{t}</div>')
    if k == 'nut':
        return f'<div class="nut" style="font-size:{s}em">{t}<svg viewBox="0 0 24 24"><path d="M5 12h13M12.5 6l6 6-6 6" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
    if k != 'nho': sys.exit(f'kieu "{k}" không có. Chọn: lon · lon-trang · dai · dai-toi · nho · y · nut')
    return f'<div class="nho" style="font-size:{s}em">{t}</div>'

def dung(c, goc):
    W, H, m, mt = c['W'], c['H'], c.get('mau', '#EB4B28'), c.get('mau_toi', '#171B22')
    lg = c.get('logo')
    logo = ''
    if lg:
        the = (f"background:#fff;padding:{int(lg['rong']*.06)}px {int(lg['rong']*.08)}px;border-radius:{int(lg['rong']*.05)}px;"
               "box-shadow:0 8px 22px rgba(15,25,45,.22);box-sizing:content-box") if lg.get('the') else ''
        logo = f'<img class="logo" src="{uri(goc, lg["tep"])}" style="left:{lg["x"]}px;top:{lg["y"]}px;width:{lg["rong"]}px;{the}">'
    web = (f'<div class="web"><svg viewBox="0 0 24 24" fill="none" stroke="{m}" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
           f'<path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>{html.escape(c["web"])}</div>') if c.get('web') else ''
    mn = c.get('mau_nhan', m); toi = bool(c.get('nen_toi'))
    def sang(h):  # màu sáng hay tối → chọn chữ đặt trên nó (đen/trắng)
        h = h.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else (0, 0, 0)
        return r * .299 + g * .587 + b * .114 > 150
    tn = mt if sang(mn) else '#fff'
    kc = c.get('kieu_chu', 'nghieng-dam')
    if kc not in KIEU_CHU: sys.exit(f'kieu_chu "{kc}" không có. Chọn: ' + ' · '.join(KIEU_CHU))
    nho_css = ('.nho{font-weight:700;color:#fff;text-shadow:0 1px 10px rgba(0,0,0,.75),0 0 3px rgba(0,0,0,.5)}' if c.get('nen_toi')
               else '.nho{font-weight:700;color:var(--t);text-shadow:0 1px 8px rgba(255,255,255,.7)}')
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,700;0,800;0,900;1,800;1,900&family=Playfair+Display:ital,wght@0,600;0,700;0,800&display=swap" rel="stylesheet">
<style>
:root{{--m:{m};--t:{mt};--n:{mn};--tn:{tn};--c:{'#fff' if toi else mt};--nc:{mn if toi else m}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:url("{uri(goc, c['nen'])}") {c.get('nen_vi_tri', 'center')}/cover no-repeat;font-family:'Be Vietnam Pro',Arial,sans-serif;position:relative}}
.logo{{position:absolute;z-index:2}}
.khoi{{position:absolute;{c['khoi']};font-size:{c['co_chu']}px;display:flex;flex-direction:column;z-index:1;
  align-items:{'flex-end' if c.get('canh') == 'phai' else 'flex-start'};gap:.12em}}
.khoi::before{{content:'';position:absolute;inset:-18% -22% -18% -30%;z-index:-1;
  background:radial-gradient(closest-side,rgba(255,255,255,{c.get('suong', .45)}),rgba(255,255,255,0))}}
.h{{position:relative;font-weight:900;font-style:italic;text-transform:uppercase;line-height:1.1;white-space:nowrap;padding:.2em .08em 0}}
.h::before{{content:attr(data-t);position:absolute;left:.08em;top:.2em;color:#fff;-webkit-text-stroke:.11em #fff;z-index:0;
  filter:drop-shadow(0 .06em 0 color-mix(in srgb,var(--m) 55%,#000)) drop-shadow(0 .14em .16em rgba(15,25,45,.35))}}
.h span{{position:relative;z-index:1;color:transparent;-webkit-background-clip:text;background-clip:text;
  background-image:linear-gradient(180deg,color-mix(in srgb,var(--m) 45%,#FFE3A0) 0%,var(--m) 55%,color-mix(in srgb,var(--m) 70%,#000) 100%)}}
.lon-trang::before{{-webkit-text-stroke:.09em var(--m);color:var(--m)}}
.lon-trang span{{background-image:linear-gradient(180deg,#fff 0%,#F7F8FA 55%,#DDE2EC 100%)}}
.bang{{display:inline-flex;align-items:center;gap:.14em;transform:skewX(-14deg);margin:.1em 0 .1em .2em}}
.bang i{{display:block;width:.16em;height:1.5em;background:var(--m)}}
.bang b{{display:block;padding:.18em .55em .22em;font-weight:800;text-transform:uppercase;white-space:nowrap;color:#fff;
  background:linear-gradient(90deg,var(--m),color-mix(in srgb,var(--m) 80%,#000));box-shadow:0 .12em .3em rgba(15,25,45,.3)}}
.dai-toi i{{background:var(--t)}} .dai-toi b{{background:linear-gradient(90deg,var(--t),color-mix(in srgb,var(--t) 80%,#fff))}}
{nho_css}
.y{{display:flex;align-items:center;gap:.5em;font-weight:700;white-space:nowrap;color:var(--c);margin-top:.28em;
  text-shadow:{'0 1px 8px rgba(0,0,0,.55)' if toi else '0 1px 8px rgba(255,255,255,.7)'}}}
.y svg{{width:1.25em;height:1.25em;flex:none}} .y circle{{fill:var(--n)}} .y path{{stroke:var(--tn)}}
.nut{{display:inline-flex;align-items:center;gap:.5em;margin-top:.7em;padding:.5em 1.05em .54em;border-radius:999px;font-weight:800;white-space:nowrap;
  background:var(--n);color:var(--tn);box-shadow:0 .25em .7em rgba(0,0,0,.28)}}
.nut svg{{width:1.05em;height:1.05em;stroke:var(--tn)}}
{KIEU_CHU[kc]}
.web{{position:absolute;right:{c.get('web_x', 40)}px;bottom:{c.get('web_y', 36)}px;font:700 {c.get('web_co', 26)}px 'Be Vietnam Pro',Arial;
  color:var(--t);background:#fff;border-radius:999px;padding:.38em .9em .38em .5em;display:flex;align-items:center;gap:.4em;
  box-shadow:0 6px 18px rgba(15,25,45,.25)}}
.web svg{{width:1.2em;height:1.2em}}
</style></head><body>{logo}<div class="khoi">{''.join(dong(d) for d in c['dong'])}</div>{web}</body></html>'''

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit('Cách chạy: python dat-chu.py cau-hinh.json [ten-anh ...]')
    tep = os.path.abspath(sys.argv[1]); goc = os.path.dirname(tep)
    cfg = json.load(open(tep, encoding='utf-8')); chrome = tim_chrome()
    ra = os.path.join(goc, 'ra'); os.makedirs(ra, exist_ok=True)
    for ten in (sys.argv[2:] or [k for k in cfg if not k.startswith('_')]):
        c = cfg[ten]; hp = os.path.join(ra, ten + '.html'); png = os.path.join(ra, ten + '.png')
        open(hp, 'w', encoding='utf-8').write(dung(c, goc))
        loi = chup(chrome, hp, png, c['W'], c['H'])
        if loi: sys.exit(f'Chrome không chụp được {ten}: ' + loi)
        print('ra', png)
        try:
            from PIL import Image
            jpg = os.path.join(ra, ten + '.jpg'); Image.open(png).convert('RGB').save(jpg, quality=92); print('ra', jpg)
        except ImportError:
            print('Cảnh báo: thiếu Pillow nên chưa xuất .jpg (chỉ có PNG). Cài: pip install pillow')
