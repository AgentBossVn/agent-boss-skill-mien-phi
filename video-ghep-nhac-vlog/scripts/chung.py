# Phần dùng chung cho mọi kiểu video: chạy lệnh, đọc thông tin video, tìm font, đọc preset + hồ sơ thương hiệu.
import json, os, subprocess, sys

for _s in (sys.stdout, sys.stderr):   # Windows: in tiếng Việt không bị vỡ chữ
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

W, H, FPS = 1080, 1920, 30
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # thư mục skill (chứa SKILL.md)
NHA = os.path.expanduser(os.environ.get('AGENT_BOSS_HOME', '~/.agent-boss'))  # dữ liệu riêng của người dùng (dùng chung mọi skill Agent Boss), cập nhật không đụng tới
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-r', str(FPS), '-pix_fmt', 'yuv420p']
AENC = ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2']


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise SystemExit(f'Lỗi khi chạy: {" ".join(cmd[:6])}...\n{r.stderr[-1500:]}')
    return r


def doc_json(p, mac_dinh=None):
    if p and os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return {} if mac_dinh is None else mac_dinh


def ghi_json(p, d):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def thong_tin(path):
    """Độ dài, khung hình, có tiếng hay không."""
    r = run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', path])
    d = json.loads(r.stdout)
    v = next((s for s in d['streams'] if s['codec_type'] == 'video'), None)
    if v is None:
        raise SystemExit(f'{path}: không có hình')
    w, h = int(v['width']), int(v['height'])
    rot = int((v.get('tags') or {}).get('rotate', 0) or 0)
    for sd in v.get('side_data_list') or []:
        rot = int(sd.get('rotation', rot) or rot)
    if abs(rot) in (90, 270):
        w, h = h, w
    return {'dai': float(d['format']['duration']), 'rong': w, 'cao': h,
            'co_tieng': any(s['codec_type'] == 'audio' for s in d['streams'])}


def preset():
    return doc_json(os.path.join(SKILL_DIR, 'preset.json'))


def thuong_hieu(duong_dan=None):
    """Hồ sơ thương hiệu của người dùng: nằm ngoài thư mục skill để cập nhật skill không xoá mất."""
    mac_dinh = {'ten': '', 'cau_ket': 'Theo dõi để xem thêm', 'mau_chinh': '#111111', 'mau_nhan': '#FFD21F',
                'mau_chu': '#FFFFFF', 'logo': None, 'font': None, 'nhac': None}
    p = duong_dan or os.path.join(NHA, 'thuong-hieu.json')
    mac_dinh.update(doc_json(p))
    return mac_dinh


def mau(hex_, a=255):
    h = hex_.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def tim_font(ten=None):
    """Tìm font theo thứ tự: đường dẫn trong hồ sơ, font kèm skill, font đã tải về máy, font hệ thống có tiếng Việt."""
    ung_vien = []
    if ten:
        ung_vien += [os.path.expanduser(ten), os.path.join(SKILL_DIR, 'assets', 'fonts', ten), os.path.join(NHA, 'fonts', ten)]
    ung_vien += [os.path.join(SKILL_DIR, 'assets', 'fonts', 'BeVietnamPro-Black.ttf'), os.path.join(NHA, 'fonts', 'BeVietnamPro-Black.ttf'),
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
                 '/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf']
    for p in ung_vien:
        if p and os.path.exists(p):
            return p
    raise SystemExit('Không tìm thấy font có tiếng Việt. Chạy: python3 scripts/kiem_tra.py --cai-font')


def duong_ff(p):
    """Đường dẫn ghi vào file danh sách của ffmpeg: dùng / cho cả Windows."""
    return p.replace('\\', '/')


def log(*a):
    print(*a, file=sys.stderr)
