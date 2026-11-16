# Đóng gói bộ skill video: chép phần lõi (core/) vào từng kiểu (kieu/<tên>/) → <gốc kho>/video-<tên>/ là skill hoàn chỉnh.
# Chạy: python3 nguon/video/dong-goi.py   (Windows: py -3 ...) sau MỖI lần sửa core hoặc kiểu.
# Phát hành: tăng số trong phien-ban.json → đóng gói → python3 nguon/video/kiem-thu/chay.py → đẩy lên main.
# Thư mục video-*/ ở gốc kho là thứ người dùng cài: KHÔNG sửa tay, sửa ở nguon/video/ rồi đóng gói lại.
import json, os, re, shutil

NGUON = os.path.dirname(os.path.abspath(__file__))
KHO = os.path.dirname(os.path.dirname(NGUON))
PB = json.load(open(os.path.join(NGUON, 'phien-ban.json'), encoding='utf-8'))
CHUNG = open(os.path.join(NGUON, 'core', 'HUONG-DAN-CHUNG.md'), encoding='utf-8').read()

for kieu in sorted(os.listdir(os.path.join(NGUON, 'kieu'))):
    src = os.path.join(NGUON, 'kieu', kieu)
    ten = 'video-' + kieu
    if ten not in PB:
        raise SystemExit(f'phien-ban.json thiếu {ten}')
    dich = os.path.join(KHO, ten)
    shutil.rmtree(dich, ignore_errors=True)
    shutil.copytree(os.path.join(NGUON, 'core', 'scripts'), os.path.join(dich, 'scripts'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(os.path.join(src, 'preset.json'), dich)
    rieng = open(os.path.join(src, 'kieu.md'), encoding='utf-8').read()
    # gắn tác giả + phiên bản vào đầu SKILL.md (kiem_tra.py đọc số này để báo cập nhật)
    rieng = re.sub(r'\n---\n', f'\nmetadata:\n  author: Mai Xuân Đạt — Agent Boss\n  version: "{PB[ten]}"\n---\n', rieng, count=1)
    with open(os.path.join(dich, 'SKILL.md'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(rieng.rstrip() + '\n\n' + CHUNG)
    print(f'{ten} {PB[ten]}')
