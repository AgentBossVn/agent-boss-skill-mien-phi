# Kiểm tra trước khi dựng: máy đủ công cụ chưa + có bản cập nhật không. KHÔNG BAO GIỜ làm hỏng việc dựng video:
# lỗi mạng, GitHub chậm... đều bỏ qua im lặng.
# Chạy: python3 scripts/kiem_tra.py            (Windows: py -3 scripts/kiem_tra.py) → in trạng thái (JSON)
#       python3 scripts/kiem_tra.py --cai-font → tải font Be Vietnam Pro về ~/.agent-boss/fonts
import json, os, re, shutil, sys, time, urllib.request
from chung import SKILL_DIR, NHA, doc_json, ghi_json

REPO = 'AgentBossVn/agent-boss-skills'
FONT_URL = 'https://github.com/google/fonts/raw/main/ofl/bevietnampro/BeVietnamPro-Black.ttf'
WIN = sys.platform == 'win32'
PY = 'py -3' if WIN else 'python3'


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
    for mod, goi in (('PIL', 'pillow'), ('numpy', 'numpy')):
        try:
            __import__(mod)
        except ImportError:
            thieu.append(f'{PY} -m pip install --user {goi}')
    tuy_chon = []
    for mod, goi, de in (('faster_whisper', 'faster-whisper', 'làm phụ đề từ lời nói'), ('edge_tts', 'edge-tts', 'giọng đọc AI tiếng Việt')):
        try:
            __import__(mod)
        except ImportError:
            tuy_chon.append(f'{PY} -m pip install --user {goi}  ({de})')
    return thieu, tuy_chon


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
    kq['skill_khac_chua_cai'] = [d for d in c.get('ds', []) if not d.startswith(('.', 'nguon', 'kiem-thu')) and d not in da_co][:6]
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
    thieu, tuy_chon = moi_truong()
    try:
        cn = cap_nhat()
    except Exception:
        cn = None
    print(json.dumps({'skill': TEN, 'phien_ban': PHIEN_BAN, 'he_dieu_hanh': sys.platform, 'lenh_python': PY,
                      'thieu_bat_buoc': thieu, 'thieu_tuy_chon': tuy_chon, 'cap_nhat': cn}, ensure_ascii=False, indent=2))
