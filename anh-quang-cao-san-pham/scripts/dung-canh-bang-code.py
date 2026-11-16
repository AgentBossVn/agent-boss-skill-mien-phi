# Dựng CẢNH có sản phẩm thật bằng code (đường "Claude tự dựng": không AI vẽ, 0đ): phông + bục + ánh sáng + bóng + phản chiếu,
# sản phẩm là ảnh thật đã tách nền nên đúng 100%. Dựng bằng HTML/CSS rồi chụp bằng Chrome/Edge (cùng trình duyệt dat-chu.py dùng).
# Thay cho cặp ve-nen-bang-code.py + ghep-san-pham-that.py ở đường này (cặp đó ra nền chuyển màu phẳng, sản phẩm nhỏ, nhìn như dán).
# Chạy: python dung-canh-bang-code.py --vat phang/vat.png --mau-chinh "#b01820" [--mau-nhan "#e8b848"] --kieu san-khau
#           --co 1080x1350 1920x1080 1080x1920 --ra ve/ [--cao 0.5] [--tam-x 0.5] [--day-y 0.84] [--nghieng -5] [--ten canh-1]
#   --kieu san-khau : phông tối, đèn rọi từ trên, bục tròn, phản chiếu (đồ uống, điện máy, xe, đồ nam, hàng cao cấp)
#          sang-sach: tường sáng + sàn, vòm màu nhạt sau sản phẩm, bục trắng (mỹ phẩm, mẹ & bé, gia dụng, thực phẩm sạch)
#          mau-khoi : nền màu thương hiệu đậm, mảng tròn + dải chéo + lưới chấm, sản phẩm nổi có bóng dày (hàng tiêu dùng, đồ ăn vặt, khuyến mãi)
#   --mau-chinh = màu lấy từ logo/bao bì hãng · --mau-nhan = màu thứ hai trên bao bì (không ghi: san-khau dùng vàng nhạt, kiểu khác dùng sắc nhạt của màu chính)
#   Không ghi --cao/--tam-x/--day-y: ảnh dọc đặt sản phẩm giữa-dưới (chữ ở trên), ảnh ngang đặt bên phải (chữ bên trái).
#   → <ra>/<ten>-<rộng>x<cao>.png + in VÙNG CHỪA CHỮ để điền "khoi" cho dat-chu.py.
import sys
if sys.platform == 'win32':  # in tiếng Việt qua ống không vỡ (Windows mặc định cp1252)
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import argparse, importlib.util, os, re
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--vat', required=True, help='PNG sản phẩm đã tách nền (trong suốt)')
ap.add_argument('--mau-chinh', required=True); ap.add_argument('--mau-nhan', default='')
ap.add_argument('--kieu', default='san-khau', choices=['san-khau', 'sang-sach', 'mau-khoi'])
ap.add_argument('--co', nargs='+', required=True, help='vd 1080x1350'); ap.add_argument('--ra', required=True)
ap.add_argument('--cao', type=float, default=0, help='chiều cao sản phẩm / chiều cao ảnh')
ap.add_argument('--tam-x', type=float, default=0); ap.add_argument('--day-y', type=float, default=0)
ap.add_argument('--nghieng', type=float, default=0, help='xoay sản phẩm vài độ (chỉ hợp kiểu mau-khoi, vd -5)')
ap.add_argument('--ten', default='', help='tên tệp ra (mặc định canh-<kieu>)')
a = ap.parse_args()
for m in (a.mau_chinh, a.mau_nhan):
    if m and not re.fullmatch(r'#[0-9a-fA-F]{6}', m): sys.exit(f'Màu "{m}" phải dạng #rrggbb')

day = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('dat_chu', os.path.join(day, 'dat-chu.py')); dc = importlib.util.module_from_spec(sp); sp.loader.exec_module(dc)
chrome = dc.tim_chrome()
os.makedirs(a.ra, exist_ok=True)
ten = a.ten or f'canh-{a.kieu}'

vat = Image.open(a.vat).convert('RGBA')
vat = vat.crop(vat.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())  # cắt sát phần có sản phẩm
vat_tep = os.path.join(os.path.abspath(a.ra), f'.{ten}-vat.png'); vat.save(vat_tep)
VAT = Path(vat_tep).as_uri()
M = a.mau_chinh; N = a.mau_nhan or ('#ffd98a' if a.kieu == 'san-khau' else '')


def canh(W, H):
    ngang = W > H * 1.2
    cao = a.cao or (0.60 if ngang else 0.40 if H > W * 1.5 else 0.48)
    tam = a.tam_x or (0.72 if ngang else 0.5)
    dy = a.day_y or (0.86 if ngang else 0.80 if H > W * 1.5 else 0.85)
    h = round(H * cao); w = round(vat.width * h / vat.height)
    rong_toi_da = W * (0.44 if ngang else 0.72)  # sản phẩm bè ngang (nồi, hộp dẹt): bó theo chiều rộng
    if w > rong_toi_da: w = round(rong_toi_da); h = round(vat.height * w / vat.width)
    ti = h / vat.height
    if ti > 1:  # không bao giờ phóng to quá ảnh gốc
        h = vat.height; w = vat.width; ti = 1
        print(f'CHÚ Ý {W}x{H}: ảnh sản phẩm chỉ {vat.width}x{vat.height} nên máy giữ cỡ gốc (không phóng to). Muốn sản phẩm to hơn → xin ảnh hãng to + nét hơn.')
    elif ti > 0.8:
        print(f'CẢNH BÁO {W}x{H}: sản phẩm hiện bằng {ti:.0%} cỡ ảnh gốc ({vat.width}x{vat.height}) → dễ MỜ. Cắt phóng to soát độ nét; mờ thì hạ --cao xuống ≤ {0.8 * vat.height / H:.2f} hoặc xin ảnh to hơn.')
    cx = round(W * tam); by = round(H * dy); x = cx - w // 2; y = by - h
    u = min(W, H) / 1080  # đơn vị co giãn theo cỡ ảnh
    bw = round(max(w * 1.55, 420 * u)); bh = round(bw * 0.20); bd = round(bw * 0.075)  # bục: rộng, dày mặt elip, cao thân
    by0 = by - bh // 2 + round(bh * 0.08)  # đỉnh elip mặt bục: đáy sản phẩm nằm gần giữa mặt bục
    xoay = f'transform:rotate({a.nghieng}deg);transform-origin:50% 90%;' if a.nghieng else ''
    vat_img = f'<img class="vat" src="{VAT}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{xoay}">'
    pc = (f'<img class="pc" src="{VAT}" style="left:{x}px;top:{by - 1}px;width:{w}px;height:{h}px">')  # phản chiếu: lật dọc, mờ dần
    css_chung = f''':root{{--m:{M};--n:{N or M};--u:{u:.3f}px}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative}}
div,img{{position:absolute}}
.vat{{z-index:6}}
.pc{{z-index:4;transform:scaleY(-1);transform-origin:50% 0;-webkit-mask-image:linear-gradient(to top,rgba(0,0,0,.42),rgba(0,0,0,0) 26%);mask-image:linear-gradient(to top,rgba(0,0,0,.42),rgba(0,0,0,0) 26%);filter:blur(calc(var(--u)*1.5))}}
.hat{{inset:0;z-index:9;opacity:.05;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")}}'''
    buc_vi_tri = f'left:{cx - bw // 2}px;width:{bw}px'

    if a.kieu == 'san-khau':
        css = f'''body{{background:
  radial-gradient(ellipse {W * .75:.0f}px {H * .62:.0f}px at {cx}px {y + h * .45:.0f}px,color-mix(in srgb,var(--m) 88%,#fff) 0%,color-mix(in srgb,var(--m) 62%,#000) 42%,color-mix(in srgb,var(--m) 22%,#050505) 100%)}}
.san{{left:0;right:0;top:{by0 + bh // 2}px;bottom:0;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,.72))}}
.san::before{{content:'';position:absolute;left:0;right:0;top:0;height:calc(var(--u)*2);background:linear-gradient(90deg,transparent,color-mix(in srgb,var(--n) 55%,transparent) {tam * 100:.0f}%,transparent)}}
.den{{z-index:2;left:{cx - w * 1.5:.0f}px;width:{w * 3:.0f}px;top:0;height:{by0 + bh // 2}px;
  background:linear-gradient(180deg,rgba(255,255,255,.26),rgba(255,255,255,.03) 85%,transparent);
  clip-path:polygon(40% 0,60% 0,100% 100%,0 100%);filter:blur(calc(var(--u)*26))}}
.quang{{z-index:2;left:{cx - w * .95:.0f}px;top:{y + h * .12:.0f}px;width:{w * 1.9:.0f}px;height:{h * .9:.0f}px;border-radius:50%;
  background:radial-gradient(closest-side,color-mix(in srgb,var(--n) 55%,transparent),transparent);opacity:.55}}
.vong{{z-index:2;left:{cx - h * .62:.0f}px;top:{y + h * .46 - h * .62:.0f}px;width:{h * 1.24:.0f}px;height:{h * 1.24:.0f}px;border-radius:50%;
  border:calc(var(--u)*3) solid color-mix(in srgb,var(--n) 70%,transparent);-webkit-mask-image:linear-gradient(200deg,#000 18%,transparent 62%);mask-image:linear-gradient(200deg,#000 18%,transparent 62%)}}
.buc-than{{z-index:3;{buc_vi_tri};top:{by0 + bh // 2}px;height:{bd + bh // 2}px;border-radius:0 0 {bw // 2}px {bw // 2}px/0 0 {bh // 2}px {bh // 2}px;
  background:linear-gradient(90deg,color-mix(in srgb,var(--m) 30%,#000),color-mix(in srgb,var(--m) 70%,#222) 38%,color-mix(in srgb,var(--m) 55%,#000) 62%,color-mix(in srgb,var(--m) 18%,#000));
  box-shadow:0 calc(var(--u)*26) calc(var(--u)*50) rgba(0,0,0,.6)}}
.buc-mat{{z-index:3;{buc_vi_tri};top:{by0}px;height:{bh}px;border-radius:50%;
  background:radial-gradient(ellipse at 50% 35%,color-mix(in srgb,var(--m) 70%,#fff) 0%,color-mix(in srgb,var(--m) 80%,#000) 75%);
  box-shadow:inset 0 0 0 calc(var(--u)*2) color-mix(in srgb,var(--n) 60%,transparent),0 0 calc(var(--u)*40) color-mix(in srgb,var(--n) 35%,transparent)}}
.bong{{z-index:5;left:{x - w * .04:.0f}px;top:{by - h * .022:.0f}px;width:{w * 1.08:.0f}px;height:{h * .05:.0f}px;border-radius:50%;background:rgba(0,0,0,.6);filter:blur(calc(var(--u)*9))}}
.pc{{clip-path:ellipse({bw / 2:.0f}px {bh / 2:.0f}px at {w / 2:.0f}px {by0 + bh / 2 - by + 1:.0f}px)}}
.bui i{{position:absolute;border-radius:50%;background:radial-gradient(closest-side,color-mix(in srgb,var(--n) 80%,#fff),transparent);opacity:.5}}'''
        bui = ''.join(f'<i style="left:{cx + dx * w:.0f}px;top:{y + dyy * h:.0f}px;width:{s * u:.0f}px;height:{s * u:.0f}px;opacity:{o}"></i>'
                      for dx, dyy, s, o in ((-1.05, .1, 30, .5), (-.85, .55, 14, .6), (.95, .22, 20, .55), (1.12, .6, 36, .35), (-.62, -.12, 10, .7), (.7, -.06, 16, .5)))
        than = f'<div class="san"></div><div class="den"></div><div class="quang"></div><div class="vong"></div><div class="buc-than"></div><div class="buc-mat"></div>{pc}<div class="bong"></div><div class="bui" style="inset:0;z-index:2">{bui}</div>{vat_img}'
    elif a.kieu == 'sang-sach':
        vr = round(max(w * 1.5, h * .78)); vt = round(y - h * .16)  # vòm sau sản phẩm
        css = f'''body{{background:linear-gradient(180deg,color-mix(in srgb,var(--m) 7%,#fbf8f3) 0%,color-mix(in srgb,var(--m) 13%,#f3ece2) 100%)}}
.san{{left:0;right:0;top:{by0 + bh // 2 - round(H * .03)}px;bottom:0;z-index:1;background:linear-gradient(180deg,color-mix(in srgb,var(--m) 16%,#e9dfd2),color-mix(in srgb,var(--m) 8%,#f7f1e8) 55%)}}
.san::before{{content:'';position:absolute;left:0;right:0;top:0;height:{round(H * .05)}px;background:linear-gradient(180deg,rgba(60,40,20,.10),transparent)}}
.vom{{z-index:2;left:{cx - vr // 2}px;top:{vt}px;width:{vr}px;height:{by0 + bh // 2 - vt}px;border-radius:{vr // 2}px {vr // 2}px 0 0;
  background:linear-gradient(180deg,color-mix(in srgb,var(--m) 46%,#fff),color-mix(in srgb,var(--m) 26%,#fff));box-shadow:inset 0 0 calc(var(--u)*60) rgba(255,255,255,.45)}}
.cham{{z-index:2;left:{cx + vr * .36:.0f}px;top:{vt + (by0 - vt) * .08:.0f}px;width:{vr * .30:.0f}px;height:{vr * .30:.0f}px;border-radius:50%;background:color-mix(in srgb,var(--n) 72%,#fff);box-shadow:0 calc(var(--u)*14) calc(var(--u)*30) rgba(60,40,20,.12)}}
.cham2{{z-index:2;left:{cx - vr * .66:.0f}px;top:{vt + (by0 - vt) * .52:.0f}px;width:{vr * .16:.0f}px;height:{vr * .16:.0f}px;border-radius:50%;border:calc(var(--u)*4) solid color-mix(in srgb,var(--m) 55%,#fff)}}
.buc-than{{z-index:3;{buc_vi_tri};top:{by0 + bh // 2}px;height:{bd + bh // 2}px;border-radius:0 0 {bw // 2}px {bw // 2}px/0 0 {bh // 2}px {bh // 2}px;
  background:linear-gradient(90deg,#e6ddd2,#fbf8f4 35%,#f1e9df 65%,#d9cec1);box-shadow:0 calc(var(--u)*24) calc(var(--u)*46) rgba(70,45,20,.22)}}
.buc-mat{{z-index:3;{buc_vi_tri};top:{by0}px;height:{bh}px;border-radius:50%;background:radial-gradient(ellipse at 40% 30%,#fff,#f4ede4 80%)}}
.bong{{z-index:5;left:{x - w * .02:.0f}px;top:{by - h * .02:.0f}px;width:{w * 1.2:.0f}px;height:{h * .05:.0f}px;border-radius:50%;background:rgba(60,35,15,.42);filter:blur(calc(var(--u)*10))}}
.pc{{opacity:.5;clip-path:ellipse({bw / 2:.0f}px {bh / 2:.0f}px at {w / 2:.0f}px {by0 + bh / 2 - by + 1:.0f}px)}}'''
        than = f'<div class="san"></div><div class="vom"></div><div class="cham"></div><div class="cham2"></div><div class="buc-than"></div><div class="buc-mat"></div>{pc}<div class="bong"></div>{vat_img}'
    else:  # mau-khoi
        r = round(max(w, h) * 1.12)
        css = f'''body{{background:linear-gradient(155deg,color-mix(in srgb,var(--m) 86%,#fff) 0%,var(--m) 45%,color-mix(in srgb,var(--m) 72%,#000) 100%)}}
.dai{{z-index:1;left:-20%;width:140%;top:{by - h * .30:.0f}px;height:{h * .46:.0f}px;transform:rotate(-8deg);background:linear-gradient(90deg,color-mix(in srgb,var(--m) 62%,#000),color-mix(in srgb,var(--m) 80%,#000))}}
.tron{{z-index:2;left:{cx - r // 2}px;top:{y + h * .5 - r / 2:.0f}px;width:{r}px;height:{r}px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,color-mix(in srgb,var(--n) {'92%' if N else '34%'},#fff),color-mix(in srgb,var(--n) {'100%' if N else '50%'},#fff));box-shadow:0 calc(var(--u)*30) calc(var(--u)*70) rgba(0,0,0,.28)}}
.tron2{{z-index:2;left:{cx - r * .64:.0f}px;top:{y + h * .5 - r * .64:.0f}px;width:{r * 1.28:.0f}px;height:{r * 1.28:.0f}px;border-radius:50%;border:calc(var(--u)*3) dashed rgba(255,255,255,.45)}}
.luoi{{z-index:2;width:{260 * u:.0f}px;height:{200 * u:.0f}px;background-image:radial-gradient(rgba(255,255,255,.55) calc(var(--u)*3.2),transparent calc(var(--u)*3.6));background-size:calc(var(--u)*26) calc(var(--u)*26)}}
.vat{{filter:drop-shadow(0 calc(var(--u)*34) calc(var(--u)*30) rgba(0,0,0,.42)) drop-shadow(0 calc(var(--u)*6) calc(var(--u)*8) rgba(0,0,0,.3))}}'''
        than = (f'<div class="dai"></div><div class="tron"></div><div class="tron2"></div>'
                f'<div class="luoi" style="right:{36 * u:.0f}px;bottom:{36 * u:.0f}px"></div><div class="luoi" style="left:{36 * u:.0f}px;top:{H * .40:.0f}px;opacity:{0 if ngang else .6}"></div>{vat_img}')

    trang = f'<!doctype html><html><head><meta charset="utf-8"><style>{css_chung}\n{css}</style></head><body>{than}<div class="hat"></div></body></html>'
    if ngang: chua = f'bên trái, x từ 0 tới {max(0, x - round(w * .25))}px (rộng {max(0, x - round(w * .25)) / W:.0%} ảnh), cao cả ảnh'
    else: chua = f'phía trên, y từ 0 tới {max(0, y - round(h * .14))}px ({max(0, y - round(h * .14)) / H:.0%} chiều cao ảnh), rộng cả ảnh'
    return trang, chua, (w, h, x, y)


for co in a.co:
    W, H = (int(v) for v in co.lower().split('x'))
    trang, chua, (w, h, x, y) = canh(W, H)
    hp = os.path.join(os.path.abspath(a.ra), f'.{ten}-{W}x{H}.html'); png = os.path.join(a.ra, f'{ten}-{W}x{H}.png')
    open(hp, 'w', encoding='utf-8').write(trang)
    loi = dc.chup(chrome, hp, os.path.abspath(png), W, H)
    if loi: sys.exit(f'Chrome không chụp được {png}: ' + loi)
    os.remove(hp)
    print(f'ra {png} · sản phẩm {w}x{h} tại ({x},{y}) · VÙNG CHỪA CHỮ: {chua}')
os.remove(vat_tep)
