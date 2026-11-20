#!/usr/bin/env python3
"""Đo độ tương phản chữ/nền theo WCAG.

Chạy:  python do-tuong-phan.py "#hex1" "#hex2"            → tỉ lệ 2 màu
       python do-tuong-phan.py <thư-mục-bộ | tokens.json>  → kiểm các cặp màu mà 7 mẫu ấn phẩm sẽ dùng
Cờ --json: in JSON. Thoát mã 1 nếu cặp BẮT BUỘC không đạt (chữ chính/nền, mực/nền sáng, chữ nút/nút < 4,5; màu nhấn/nền < 3).
"""
import sys, re, json, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

# (màu trước, màu sau, mô tả, bắt buộc: None | ngưỡng)
CAC_CAP = [
    ('chu_tren_nen', 'nen', 'chữ chính trên nền màu chính', 4.5),
    ('chu_phu_tren_nen', 'nen', 'chữ phụ trên nền màu chính', 3.0),
    ('nhan', 'nen', 'chữ màu nhấn trên nền màu chính', 3.0),
    ('chu_tren_nhan', 'nhan', 'chữ trên nút màu nhấn', 4.5),
    ('chu_tren_nen', 'the', 'chữ trên thẻ nổi', 3.0),
    ('chu_phu_tren_nen', 'the', 'chữ phụ trên thẻ nổi', 3.0),
    ('muc', 'nen_sang', 'chữ mực trên nền sáng', 4.5),
    ('muc_phu', 'nen_sang', 'chữ phụ trên nền sáng', 4.5),
    ('nen', 'nen_sang', 'tiêu đề màu chính trên nền sáng', 3.0),
    ('nhan', 'nen_sang', 'chữ màu nhấn trên nền sáng', None),
]


def chuan_hex(s: str) -> str:
    s = str(s).strip().lstrip('#')
    if re.fullmatch(r'[0-9a-fA-F]{3}', s): s = ''.join(c * 2 for c in s)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', s): raise ValueError(f'"{s}" không phải mã màu hex (ví dụ #004AEF)')
    return '#' + s.upper()


def do_sang(hx: str) -> float:
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ti_le(a: str, b: str) -> float:
    la, lb = do_sang(chuan_hex(a)), do_sang(chuan_hex(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def phan(t: float) -> str:
    if t >= 4.5: return 'dùng mọi cỡ'
    if t >= 3: return 'chỉ chữ to: ≥24px thường hoặc ≥19px đậm'
    return 'CẤM dùng làm chữ'


def so_vn(x: float) -> str: return f'{x:.2f}'.replace('.', ',')


def kiem_bo(mau: dict):
    """Kiểm các cặp trong khối "mau" của tokens.json → (danh sách dòng, đạt?)"""
    dong, dat = [], True
    for tr, sau, mo_ta, bat_buoc in CAC_CAP:
        if tr not in mau or sau not in mau:
            dong.append({'cap': f'{tr}/{sau}', 'mo_ta': mo_ta, 'bo_qua': 'thiếu màu trong tokens.json'}); continue
        t = ti_le(mau[tr], mau[sau])
        d = {'cap': f'{tr}/{sau}', 'mo_ta': mo_ta, 'mau_truoc': chuan_hex(mau[tr]), 'mau_sau': chuan_hex(mau[sau]),
             'ti_le': round(t, 2), 'phan': phan(t), 'bat_buoc': bat_buoc is not None}
        if bat_buoc is not None and t < bat_buoc: d['truot'] = True; dat = False
        dong.append(d)
    return dong, dat


def doc_tokens(duong_dan: str) -> dict:
    p = Path(duong_dan).expanduser()
    if p.is_dir(): p = p / 'tokens.json'
    if not p.is_file(): raise ValueError(f'không thấy {p}')
    try: return json.loads(p.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as e: raise ValueError(f'{p} không phải JSON hợp lệ: {e}')


def main():
    ap = argparse.ArgumentParser(description='Đo tương phản WCAG')
    ap.add_argument('dau_vao', nargs='+'); ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    try:
        if len(a.dau_vao) == 2 and all(re.fullmatch(r'#?[0-9a-fA-F]{3}([0-9a-fA-F]{3})?', x) for x in a.dau_vao):
            t = ti_le(*a.dau_vao)
            if a.json: print(json.dumps({'ti_le': round(t, 2), 'phan': phan(t)}, ensure_ascii=False))
            else: print(f'{chuan_hex(a.dau_vao[0])} / {chuan_hex(a.dau_vao[1])}: {so_vn(t)} : 1 — {phan(t)}')
            return
        if len(a.dau_vao) != 1: raise ValueError('cách gọi: do-tuong-phan.py "#hex1" "#hex2"  hoặc  do-tuong-phan.py <thư-mục-bộ>')
        mau = doc_tokens(a.dau_vao[0]).get('mau')
        if not isinstance(mau, dict): raise ValueError('tokens.json thiếu khối "mau"')
        dong, dat = kiem_bo(mau)
    except ValueError as e:
        print(f'LỖI: {e}'); sys.exit(2)
    if a.json: print(json.dumps({'dat': dat, 'cac_cap': dong}, ensure_ascii=False, indent=2))
    else:
        print('| Cặp (chữ / nền) | Dùng cho | Tỉ lệ | Phán |\n|---|---|---|---|')
        for d in dong:
            if 'bo_qua' in d: print(f'| {d["cap"]} | {d["mo_ta"]} | — | bỏ qua ({d["bo_qua"]}) |'); continue
            cam = ' ⚠ KHÔNG ĐẠT (bắt buộc)' if d.get('truot') else ''
            print(f'| {d["cap"]} {d["mau_truoc"]}/{d["mau_sau"]} | {d["mo_ta"]} | {so_vn(d["ti_le"])} | {d["phan"]}{cam} |')
        print('\n' + ('ĐẠT các cặp bắt buộc.' if dat else 'KHÔNG ĐẠT: sửa màu rồi đo lại.'))
    sys.exit(0 if dat else 1)


if __name__ == '__main__':
    main()
