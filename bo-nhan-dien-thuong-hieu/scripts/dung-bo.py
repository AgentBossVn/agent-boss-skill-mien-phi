#!/usr/bin/env python3
"""Dựng bộ nhận diện từ tokens.json: điền 7 mẫu ấn phẩm vào <bộ>/mau/ + dựng <bộ>/guideline.html
+ cập nhật hồ sơ chung ~/.agent-boss/thuong-hieu.json (dùng chung với các skill video).

Chạy:  python dung-bo.py <thư-mục-bộ> [--khong-ho-so]
Thư mục bộ cần có: tokens.json (+ logo/ theo đường dẫn trong tokens.json; tùy chọn DESIGN.md).
Chạy lại được nhiều lần (ghi đè mau/ và guideline.html). Có ảnh mau/xem-truoc/*.png (do chup-anh.py chụp) thì guideline dùng ảnh,
chưa có thì dùng khung xem thu nhỏ: chụp ảnh xong nên chạy dung-bo lại để guideline có ảnh.
"""
import sys, re, json, html, argparse, importlib.util
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

AQ = Path(__file__).resolve().parent
MAU_GOC = AQ.parent / 'mau'
HEX = re.compile(r'#[0-9a-fA-F]{6}')
KHOA_MAU = ['nen', 'chu_tren_nen', 'chu_phu_tren_nen', 'nhan', 'chu_tren_nhan', 'the', 'nen_sang', 'muc', 'muc_phu']
VAI_TRO = {'nen': 'Nền chính (chiếm phần lớn ấn phẩm)', 'chu_tren_nen': 'Chữ chính trên nền màu chính',
           'chu_phu_tren_nen': 'Chữ phụ trên nền màu chính', 'nhan': 'Màu nhấn: 1 dòng tiêu đề, nút, chấm (rất ít)',
           'chu_tren_nhan': 'Chữ trên nút màu nhấn', 'the': 'Thẻ nổi trên nền màu chính', 'nen_sang': 'Nền sáng (tài liệu, slide nội dung)',
           'muc': 'Chữ trên nền sáng', 'muc_phu': 'Chữ phụ trên nền sáng'}
TEN_MAU = ['bai-dang-4x5', 'story-9x16', 'banner-ngang', 'slide-bia', 'slide-noi-dung', 'tai-lieu-a4', 'chu-ky-email']
TEN_HIEN = {'bai-dang-4x5': 'Bài đăng 4:5', 'story-9x16': 'Story 9:16', 'banner-ngang': 'Banner ngang', 'slide-bia': 'Slide bìa',
            'slide-noi-dung': 'Slide nội dung', 'tai-lieu-a4': 'Tài liệu A4', 'chu-ky-email': 'Chữ ký email'}


class Loi(Exception):
    pass


def nap_do_tuong_phan():
    spec = importlib.util.spec_from_file_location('do_tuong_phan', AQ / 'do-tuong-phan.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def doc_va_kiem(bo: Path) -> dict:
    f = bo / 'tokens.json'
    if not f.is_file(): raise Loi(f'không thấy {f}')
    try: t = json.loads(f.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as e: raise Loi(f'tokens.json không phải JSON hợp lệ: {e}')
    loi = []
    if not isinstance(t, dict): raise Loi('tokens.json phải là một đối tượng JSON')
    if not str(t.get('ten', '')).strip(): loi.append('thiếu "ten" (tên thương hiệu)')
    mau = t.get('mau') if isinstance(t.get('mau'), dict) else {}
    if not mau: loi.append('thiếu khối "mau"')
    for k in KHOA_MAU:
        if k not in mau: loi.append(f'thiếu mau.{k}')
        elif not isinstance(mau[k], str) or not HEX.fullmatch(mau[k]): loi.append(f'mau.{k} = {mau[k]!r} không phải mã hex đủ 6 số (ví dụ #004AEF)')
    font = t.get('font') if isinstance(t.get('font'), dict) else {}
    if not str(font.get('ten', '')).strip(): loi.append('thiếu font.ten')
    elif not re.fullmatch(r'[\w .-]+', font['ten']): loi.append('font.ten chỉ gồm chữ, số, dấu cách')
    logo = t.get('logo') if isinstance(t.get('logo'), dict) else {}
    if not logo.get('tren_nen'): loi.append('thiếu logo.tren_nen')
    for k in ('tren_nen', 'tren_nen_sang', 'vuong'):
        if logo.get(k) and not (bo / logo[k]).is_file(): loi.append(f'logo.{k} trỏ tới tệp không có: {logo[k]}')
    hd = t.get('hinh_dac_trung')
    if isinstance(hd, dict) and hd.get('tep') and not (bo / hd['tep']).is_file(): loi.append(f'hinh_dac_trung.tep trỏ tới tệp không có: {hd["tep"]}')
    if loi: raise Loi('tokens.json chưa đúng:\n  - ' + '\n  - '.join(loi))
    return t


def duong_dan_tu_mau(rel: str) -> str:
    """tệp trong bộ → đường dẫn tính từ <bộ>/mau/"""
    return rel if re.match(r'(https?:|data:|/)', rel) else '../' + rel.replace('\\', '/')


def dung_bien(t: dict) -> dict:
    mau, font, logo = t['mau'], t['font'], t['logo']
    b = {f'mau.{k}': mau[k].upper() for k in KHOA_MAU}
    r, g, bl = (int(mau['nhan'][i:i + 2], 16) for i in (1, 3, 5))
    b['mau.nhan_rgb'] = f'{r},{g},{bl}'
    bo_goc = t.get('bo_goc') or {}
    b['bo_goc.nut'] = bo_goc.get('nut') or '6px'; b['bo_goc.the'] = bo_goc.get('the') or '12px'
    dam = int(font.get('dam_tieu_de') or 700)
    b['font.ten'] = font['ten']; b['font.dam_tieu_de'] = str(dam)
    b['font.css'] = f"'{font['ten']}',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"
    if font.get('google_fonts', True):
        w = ';'.join(str(x) for x in sorted({400, 500, dam}))
        b['font.link'] = f'<link href="https://fonts.googleapis.com/css2?family={font["ten"].replace(" ", "+")}:wght@{w}&display=swap" rel="stylesheet">'
    else: b['font.link'] = ''
    tn = logo['tren_nen']; sang = logo.get('tren_nen_sang') or tn; vuong = logo.get('vuong') or sang
    b['logo.tren_nen'] = duong_dan_tu_mau(tn); b['logo.tren_nen_sang'] = duong_dan_tu_mau(sang); b['logo.vuong'] = duong_dan_tu_mau(vuong)
    hd = t.get('hinh_dac_trung') if isinstance(t.get('hinh_dac_trung'), dict) else {}
    b['hinh.tep'] = duong_dan_tu_mau(hd['tep']) if hd.get('tep') else ''
    b['ten'] = html.escape(t['ten'], quote=True); b['web'] = html.escape(str(t.get('web') or ''), quote=True)
    b['cau_dinh_vi'] = html.escape(str(t.get('cau_dinh_vi') or ''), quote=True)
    return b


def dien_mau(bo: Path, t: dict) -> list:
    bien = dung_bien(t); co_hinh = bool(bien['hinh.tep'])
    ra = bo / 'mau'; ra.mkdir(exist_ok=True)
    xong = []
    for ten in TEN_MAU:
        goc = MAU_GOC / f'{ten}.html'
        if not goc.is_file(): raise Loi(f'thiếu mẫu gốc {goc}')
        s = goc.read_text(encoding='utf-8')
        if not co_hinh: s = re.sub(r'[ \t]*<!--HINH-->.*?<!--/HINH-->[ \t]*\n?', '', s, flags=re.S)
        else: s = s.replace('<!--HINH-->', '').replace('<!--/HINH-->', '')
        s = re.sub(r'\{\{\s*([a-z_.]+)\s*\}\}', lambda m: bien[m.group(1)] if m.group(1) in bien else m.group(0), s)
        con = re.findall(r'\{\{[^}]*\}\}', s)
        if con: raise Loi(f'mẫu {ten} còn chỗ trống chưa điền: {con[:3]}')
        (ra / f'{ten}.html').write_text(s, encoding='utf-8'); xong.append(ten)
    return xong


# ---------------------------------------------------------------- guideline
def md_don_gian(md: str) -> str:
    """Markdown đơn giản: tiêu đề, gạch đầu dòng, bảng, đoạn, **đậm**, `mã`."""
    def inline(x): return re.sub(r'`([^`]+)`', r'<code>\1</code>', re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html.escape(x)))
    out, lst, bang = [], False, []
    def dong_ds():
        nonlocal lst
        if lst: out.append('</ul>'); lst = False
    def dong_bang():
        nonlocal bang
        if bang:
            hang = [[c.strip() for c in l.strip().strip('|').split('|')] for l in bang if not re.fullmatch(r'\s*\|?[\s:|-]+\|?\s*', l)]
            if hang:
                out.append('<table>' + '<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in hang[0]) + '</tr>'
                           + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in h) + '</tr>' for h in hang[1:]) + '</table>')
            bang = []
    for l in md.splitlines():
        if l.strip().startswith('|'): dong_ds(); bang.append(l); continue
        dong_bang()
        m = re.match(r'(#{1,4})\s+(.*)', l)
        if m: dong_ds(); n = min(6, len(m.group(1)) + 1); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>')
        elif re.match(r'\s*[-*]\s+', l):
            if not lst: out.append('<ul>'); lst = True
            out.append('<li>' + inline(re.sub(r'^\s*[-*]\s+', '', l)) + '</li>')
        elif l.strip(): dong_ds(); out.append(f'<p>{inline(l)}</p>')
        else: dong_ds()
    dong_ds(); dong_bang()
    return '\n'.join(out)


def kho_cua(path: Path):
    m = re.search(r'<meta\s+name="kho"\s+content="(\d+)x(\d+)"', path.read_text(encoding='utf-8'))
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 1080)


def dung_guideline(bo: Path, t: dict):
    dtp = nap_do_tuong_phan(); mau = t['mau']; e = html.escape
    dong_tp, dat = dtp.kiem_bo(mau)
    o_mau = ''.join(f'<div class="o"><div class="chip" style="background:{mau[k]}"></div><b>{e(k)}</b><code>{mau[k].upper()}</code><span>{e(VAI_TRO[k])}</span></div>' for k in KHOA_MAU)
    hang_tp = ''
    for d in dong_tp:
        if 'bo_qua' in d: continue
        cls = 'x' if d['ti_le'] < 3 else ('v' if d['ti_le'] < 4.5 else 'o')
        hang_tp += (f'<tr><td><span class="mau" style="background:{d["mau_truoc"]}"></span><span class="mau" style="background:{d["mau_sau"]}"></span> {e(d["mo_ta"])}</td>'
                    f'<td class="{cls}">{dtp.so_vn(d["ti_le"])}</td><td>{e(d["phan"])}</td></tr>')
    logo = t['logo']; tn = logo['tren_nen']; sang = logo.get('tren_nen_sang') or tn; vuong = logo.get('vuong')
    kl = f'<div class="logo-o" style="background:{mau["nen"]}"><img src="{e(tn)}" alt=""><small style="color:{mau["chu_phu_tren_nen"]}">Trên nền màu chính</small></div>'
    kl += f'<div class="logo-o" style="background:{mau["nen_sang"]}"><img src="{e(sang)}" alt=""><small style="color:{mau["muc_phu"]}">Trên nền sáng</small></div>'
    if vuong: kl += f'<div class="logo-o" style="background:{mau["nen_sang"]}"><img src="{e(vuong)}" alt="" style="height:120px"><small style="color:{mau["muc_phu"]}">Biểu tượng vuông</small></div>'
    hd = t.get('hinh_dac_trung') if isinstance(t.get('hinh_dac_trung'), dict) else {}
    muc_hinh = ''
    if hd.get('tep'):
        r, g, b = (int(mau['nhan'][i:i + 2], 16) for i in (1, 3, 5))
        muc_hinh = (f'<h2>Hình đặc trưng</h2><div class="hinh-o" style="background:{mau["nen"]}"><div class="qua" style="background:radial-gradient(circle,rgba({r},{g},{b},.22) 0,transparent 70%)"></div>'
                    f'<img src="{e(hd["tep"])}" alt=""></div><p>{e(str(hd.get("mo_ta") or ""))}. Quầng sáng màu nhấn mờ chỉ đặt sau hình này.</p>')
    font = t['font']
    luoi = ''
    for ten in TEN_MAU:
        w, h = kho_cua(bo / 'mau' / f'{ten}.html'); png = bo / 'mau' / 'xem-truoc' / f'{ten}.png'
        if png.is_file(): hinh = f'<img class="tn" src="mau/xem-truoc/{ten}.png" alt="">'
        else:
            tl = 300 / w
            hinh = f'<div class="kh" style="width:300px;height:{round(h * tl)}px"><iframe src="mau/{ten}.html" style="width:{w}px;height:{h}px;transform:scale({tl:.4f})" scrolling="no" tabindex="-1"></iframe></div>'
        luoi += f'<a class="mauab" href="mau/{ten}.html">{hinh}<b>{TEN_HIEN[ten]}</b><span>{w}×{h}</span></a>'
    design = ''
    if (bo / 'DESIGN.md').is_file():
        design = '<h2>Ghi chú thiết kế (DESIGN.md)</h2><div class="md">' + md_don_gian((bo / 'DESIGN.md').read_text(encoding='utf-8', errors='replace')) + '</div>'
    gg = f'<link href="https://fonts.googleapis.com/css2?family={font["ten"].replace(" ", "+")}:wght@400;500;700&display=swap" rel="stylesheet">' if font.get('google_fonts', True) else ''
    ff = f"'{font['ten']}',system-ui,sans-serif"
    trang = f'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>Bộ nhận diện {e(t['ten'])}</title>{gg}
<style>
  * {{ box-sizing:border-box; }} body {{ margin:0; font-family:{ff}; background:{mau['nen_sang']}; color:{mau['muc']}; }}
  header {{ background:{mau['nen']}; color:{mau['chu_tren_nen']}; padding:56px 8vw; }}
  header h1 {{ margin:0 0 8px; font-size:44px; font-weight:{int(font.get('dam_tieu_de') or 700)}; }} header p {{ margin:4px 0; color:{mau['chu_phu_tren_nen']}; font-size:18px; }}
  header em {{ font-style:normal; color:{mau['nhan']}; }}
  main {{ padding:32px 8vw 64px; max-width:1200px; }} h2 {{ margin:48px 0 16px; font-size:26px; color:{mau['nen']}; }}
  .luoi {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:16px; }}
  .o {{ border:1px solid #0001; border-radius:12px; overflow:hidden; background:#fff; padding-bottom:12px; }} .o .chip {{ height:72px; border-bottom:1px solid #0001; }}
  .o b, .o code, .o span {{ display:block; padding:6px 12px 0; }} .o span {{ font-size:13px; color:{mau['muc_phu']}; }}
  table {{ border-collapse:collapse; width:100%; background:#fff; }} th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid #0001; font-size:15px; }}
  .mau {{ display:inline-block; width:18px; height:18px; border-radius:4px; border:1px solid #0003; vertical-align:middle; margin-right:2px; }}
  td.o {{ color:#0A7A3E; font-weight:700; }} td.v {{ color:#9A6200; font-weight:700; }} td.x {{ color:#C0262D; font-weight:700; }}
  .chu {{ background:#fff; border-radius:12px; padding:24px; }} .chu .t {{ font-size:40px; font-weight:{int(font.get('dam_tieu_de') or 700)}; color:{mau['nen']}; }} .chu .b {{ font-size:18px; }}
  .logos {{ display:flex; flex-wrap:wrap; gap:16px; }} .logo-o {{ border-radius:12px; padding:28px; min-width:280px; border:1px solid #0001; }}
  .logo-o img {{ height:56px; width:auto; display:block; }} .logo-o small {{ display:block; margin-top:12px; }}
  .hinh-o {{ position:relative; border-radius:12px; padding:40px; display:inline-block; }} .hinh-o img {{ position:relative; height:200px; display:block; }}
  .hinh-o .qua {{ position:absolute; inset:0; filter:blur(20px); }}
  .xem {{ display:flex; flex-wrap:wrap; gap:24px; align-items:flex-start; }} .mauab {{ text-decoration:none; color:inherit; width:300px; }}
  .mauab .tn {{ width:300px; border:1px solid #0002; border-radius:8px; display:block; }} .mauab b, .mauab span {{ display:block; margin-top:6px; }} .mauab span {{ font-size:13px; color:{mau['muc_phu']}; }}
  .kh {{ position:relative; overflow:hidden; border:1px solid #0002; border-radius:8px; }} .kh iframe {{ border:0; transform-origin:0 0; position:absolute; left:0; top:0; pointer-events:none; }}
  .md {{ background:#fff; border-radius:12px; padding:8px 24px 24px; }} .md code {{ background:#0001; padding:1px 5px; border-radius:4px; }}
</style></head><body>
<header><h1>{e(t['ten'])}</h1><p>{e(str(t.get('cau_dinh_vi') or ''))}</p><p><em>Bộ nhận diện cho AI</em> · phiên bản {e(str(t.get('phien_ban') or '1.0'))} · {e(str(t.get('ngay') or ''))} · {e(str(t.get('web') or ''))}</p></header>
<main>
<h2>Màu sắc</h2><div class="luoi">{o_mau}</div>
<h2>Độ tương phản chữ / nền (WCAG)</h2>
<table><tr><th>Cặp màu</th><th>Tỉ lệ</th><th>Dùng được thế nào</th></tr>{hang_tp}</table>
<h2>Chữ</h2><div class="chu"><p>Font: <b>{e(font['ten'])}</b> · tiêu đề đậm {int(font.get('dam_tieu_de') or 700)} · nội dung 400–500 · tối đa 3 cỡ chữ mỗi ấn phẩm.</p>
<div class="t">Tiêu đề mẫu tiếng Việt: Quản trị bằng AI</div><div class="b">Nội dung mẫu: Bộ nhận diện giúp mọi ấn phẩm trông như của cùng một công ty.</div></div>
<h2>Logo</h2><div class="logos">{kl}</div>
{muc_hinh}
<h2>Bo góc</h2><p>Nút: {e(str((t.get('bo_goc') or {}).get('nut') or '6px'))} · Thẻ: {e(str((t.get('bo_goc') or {}).get('the') or '12px'))}</p>
<h2>7 ấn phẩm mẫu</h2><div class="xem">{luoi}</div>
{design}
</main></body></html>'''
    (bo / 'guideline.html').write_text(trang, encoding='utf-8')
    return dat


# ---------------------------------------------------------------- hồ sơ chung
def ghi_ho_so(bo: Path, t: dict) -> Path:
    f = Path.home() / '.agent-boss' / 'thuong-hieu.json'
    cu = {}
    if f.is_file():
        # Hồ sơ chung còn khoá của skill khác (video…): đọc không được thì DỪNG, không ghi đè làm mất dữ liệu.
        try: cu = json.loads(f.read_text(encoding='utf-8-sig'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise Loi(f'{f} không đọc được ({e}). Không ghi đè để khỏi mất khoá của skill khác — sửa tệp đó rồi chạy lại, hoặc thêm --khong-ho-so.')
        if not isinstance(cu, dict): raise Loi(f'{f} không phải đối tượng JSON — không ghi đè. Sửa tệp rồi chạy lại, hoặc thêm --khong-ho-so.')
    cu.update({'ten': t['ten'], 'mau_chinh': t['mau']['nen'], 'mau_nhan': t['mau']['nhan'], 'mau_chu': t['mau']['chu_tren_nen'],
               'logo': str((bo / t['logo']['tren_nen']).resolve()), 'font': t['font']['ten'], 'bo_nhan_dien': str(bo.resolve())})
    f.parent.mkdir(parents=True, exist_ok=True)
    tam = f.with_suffix('.json.tam')
    tam.write_text(json.dumps(cu, ensure_ascii=False, indent=2), encoding='utf-8')
    tam.replace(f)  # ghi tạm rồi đổi tên: máy tắt giữa chừng không làm hỏng hồ sơ
    return f


def main():
    ap = argparse.ArgumentParser(description='Dựng bộ nhận diện từ tokens.json')
    ap.add_argument('bo'); ap.add_argument('--khong-ho-so', action='store_true', help='không cập nhật ~/.agent-boss/thuong-hieu.json')
    ap.add_argument('--chi-guideline', action='store_true', help='chỉ dựng lại guideline.html, KHÔNG ghi đè mau/ (giữ bản đã sửa tay)')
    a = ap.parse_args()
    bo = Path(a.bo).expanduser().resolve()
    try:
        if bo.is_file(): bo = bo.parent  # cho phép đưa thẳng tokens.json
        if not bo.is_dir(): raise Loi(f'không thấy thư mục {bo}')
        t = doc_va_kiem(bo)
        if not a.chi_guideline:
            xong = dien_mau(bo, t)
            print(f'✓ đã điền {len(xong)} mẫu vào {bo / "mau"}')
        dat = dung_guideline(bo, t)
        print(f'✓ đã dựng {bo / "guideline.html"}')
        if not dat: print('⚠ Cặp màu BẮT BUỘC chưa đạt độ tương phản — chạy do-tuong-phan.py để xem và sửa màu.')
        if not a.khong_ho_so: print(f'✓ đã cập nhật hồ sơ chung {ghi_ho_so(bo, t)}')
    except Loi as e:
        print(f'LỖI: {e}'); sys.exit(1)


if __name__ == '__main__':
    main()
