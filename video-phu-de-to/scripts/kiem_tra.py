# Kiểm tra trước khi dựng: máy đủ công cụ chưa + có bản cập nhật không. KHÔNG BAO GIỜ làm hỏng việc dựng video:
# lỗi mạng, GitHub chậm... đều bỏ qua im lặng.
# Chạy: python3 scripts/kiem_tra.py            (Windows: py -3 scripts/kiem_tra.py) → in trạng thái (JSON)
#       python3 scripts/kiem_tra.py --cai-font → tải font Be Vietnam Pro về ~/.agent-boss/fonts
#       python3 scripts/kiem_tra.py --cai [gói thêm...] → tạo Python riêng ~/.agent-boss/python + cài pillow, numpy (+ gói thêm)
import json, os, re, shutil, subprocess, sys, time, urllib.request
from chung import SKILL_DIR, NHA, PY_RIENG, PY_RIENG_DIR, doc_json, ghi_json

REPO = 'AgentBossVn/agent-boss-skills'
FONT_URL = 'https://github.com/google/fonts/raw/main/ofl/bevietnampro/BeVietnamPro-Black.ttf'
WIN = sys.platform == 'win32'
PY = 'py -3' if WIN else 'python3'
BAN_HOP = ((3, 13), (3, 12), (3, 11), (3, 10))   # faster-whisper chưa có bản cho Python mới hơn 3.13 (đo 17/11/2026 trên 3.15)
LENH_CAI = f'{PY} <SKILL>/scripts/kiem_tra.py --cai'


def dau_trang(text):
    """Đọc name + metadata.version ở đầu SKILL.md."""
    ten = re.search(r'^name:\s*(\S+)', text, re.M)
    pb = re.search(r'^\s+version:\s*"?([\d.]+)"?', text, re.M)
    return (ten.group(1) if ten else None), (pb.group(1) if pb else '0.0.0')


TEN, PHIEN_BAN = dau_trang(open(os.path.join(SKILL_DIR, 'SKILL.md'), encoding='utf-8').read())


def so(pb):
    return tuple(int(x) for x in pb.split('.') if x.isdigit())


def moi_truong():
    thieu = []
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        thieu.append('ffmpeg — Windows: winget install -e --id Gyan.FFmpeg (rồi mở lại cửa sổ lệnh) | macOS: brew install ffmpeg')
    for mod in ('PIL', 'numpy'):
        try:
            __import__(mod)
        except ImportError:
            thieu.append(LENH_CAI + '  (tạo Python riêng cho skill + cài thư viện vẽ chữ)')
            break
    tuy_chon = []
    for mod, goi, de in (('faster_whisper', 'faster-whisper', 'làm phụ đề từ lời nói'), ('edge_tts', 'edge-tts', 'giọng đọc AI tiếng Việt')):
        try:
            __import__(mod)
        except ImportError:
            tuy_chon.append(f'{LENH_CAI} {goi}  ({de})')
    if not any(os.path.exists(os.path.join(d, 'BeVietnamPro-Black.ttf')) for d in (os.path.join(SKILL_DIR, 'assets', 'fonts'), os.path.join(NHA, 'fonts'))):
        tuy_chon.append(f'{PY} <SKILL>/scripts/kiem_tra.py --cai-font  (font Be Vietnam Pro đậm, đẹp; chưa có thì chữ dùng Arial)')
    return thieu, tuy_chon


def python_hop():
    """Tìm Python 3.10–3.13 trên máy để tạo Python riêng. Không có thì trả None."""
    if sys.version_info[:2] in BAN_HOP:
        return sys.executable
    for b in BAN_HOP:
        lenh = ['py', f'-{b[0]}.{b[1]}'] if WIN else [shutil.which(f'python{b[0]}.{b[1]}')]
        if not lenh[0] or not shutil.which(lenh[0]):
            continue
        r = subprocess.run(lenh + ['-c', 'import sys; print(sys.executable)'], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
    return None


def cai(goi_them):
    """Tạo ~/.agent-boss/python (một lần) rồi cài thư viện vào đó. Python của máy không bị đụng tới."""
    if not os.path.exists(PY_RIENG):
        goc = python_hop()
        if not goc:
            raise SystemExit('Cần Python 3.12 (bản mới hơn chưa chạy được thư viện nghe lời nói). '
                             + ('Cài: winget install -e --id Python.Python.3.12 --scope user' if WIN else 'Cài: brew install python@3.12')
                             + ' rồi chạy lại lệnh này.')
        r = subprocess.run([goc, '-m', 'venv', PY_RIENG_DIR])
        if r.returncode:
            raise SystemExit('Không tạo được Python riêng (xem lỗi ở trên).')
    r = subprocess.run([PY_RIENG, '-m', 'pip', 'install', '-q', '--disable-pip-version-check', 'pillow', 'numpy', *goi_them])
    if r.returncode:
        raise SystemExit('Cài thư viện lỗi (xem lỗi ở trên).')
    print(PY_RIENG)


def lay(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'agent-boss-skill'})
    with urllib.request.urlopen(req, timeout=4) as r:
        return r.read().decode('utf-8')


def cap_nhat():
    """Mỗi ngày hỏi GitHub 1 lần: SKILL.md bản mới nhất có phiên bản cao hơn không, có skill video mới không."""
    cache = os.path.join(NHA, 'kiem-tra-cap-nhat', f'{TEN}.json')
    c = doc_json(cache)
    if time.time() - c.get('luc', 0) > 86400:
        try:
            _, moi = dau_trang(lay(f'https://raw.githubusercontent.com/{REPO}/main/{TEN}/SKILL.md'))
            try:
                ds = [x['name'] for x in json.loads(lay(f'https://api.github.com/repos/{REPO}/contents/')) if x.get('type') == 'dir']
            except Exception:
                ds = c.get('ds', [])
            c = {'luc': time.time(), 'moi': moi, 'ds': ds}
            ghi_json(cache, c)
        except Exception:
            return None
    kq = {'dang_dung': PHIEN_BAN, 'moi_nhat': c.get('moi'), 'co_ban_moi': so(c.get('moi') or '0') > so(PHIEN_BAN)}
    if kq['co_ban_moi']:
        kq['cau_cap_nhat'] = f'Cập nhật skill {TEN} từ https://github.com/{REPO}'
    cha = os.path.dirname(SKILL_DIR)   # thư mục chứa các skill đã cài
    da_co = set(os.listdir(cha)) if os.path.isdir(cha) else set()
    kq['skill_khac_chua_cai'] = [d for d in c.get('ds', []) if not d.startswith(('.', 'nguon', 'kiem-thu', 'vi-du')) and d not in da_co][:6]
    return kq


def cai_font():
    dich = os.path.join(NHA, 'fonts', 'BeVietnamPro-Black.ttf')
    os.makedirs(os.path.dirname(dich), exist_ok=True)
    urllib.request.urlretrieve(FONT_URL, dich)
    print(dich)


if __name__ == '__main__':
    if '--cai-font' in sys.argv:
        cai_font()
        sys.exit()
    if '--cai' in sys.argv:
        cai(sys.argv[sys.argv.index('--cai') + 1:])
        sys.exit()
    thieu, tuy_chon = moi_truong()
    try:
        cn = cap_nhat()
    except Exception:
        cn = None
    print(json.dumps({'skill': TEN, 'phien_ban': PHIEN_BAN, 'he_dieu_hanh': sys.platform, 'python_rieng': os.path.exists(PY_RIENG),
                      'thieu_bat_buoc': thieu, 'thieu_tuy_chon': tuy_chon, 'cap_nhat': cn}, ensure_ascii=False, indent=2))
