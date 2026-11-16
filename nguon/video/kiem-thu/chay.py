# Kiểm thử tự động: tạo video giả → chạy cả 3 kiểu → kiểm tra video ra đúng khung, đúng độ dài, có tiếng.
# Chạy trước MỖI lần phát hành: python3 nguon/video/kiem-thu/chay.py   (cần chạy nguon/video/dong-goi.py trước)
import json, os, shutil, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # nguon/video
KHO = os.path.dirname(os.path.dirname(GOC))
T = os.path.join(GOC, 'kiem-thu', '.tam')
SK = KHO   # skill đã đóng gói nằm ở gốc kho
shutil.rmtree(T, ignore_errors=True)
os.makedirs(T)


def ff(*a):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *a], check=True)


def chay(skill, *a):
    r = subprocess.run([sys.executable, os.path.join(SK, skill, 'scripts', a[0]), *a[1:]], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit(f'{skill} {a[0]} LỖI:\n{r.stdout}\n{r.stderr}')
    return r.stdout


def kiem(p, dai_min, dai_max):
    d = json.loads(subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', p],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace').stdout)
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    dai = float(d['format']['duration'])
    ok = (v['width'], v['height']) == (1080, 1920) and dai_min <= dai <= dai_max and any(s['codec_type'] == 'audio' for s in d['streams'])
    print(f"  {'OK ' if ok else 'SAI'} {os.path.basename(p)} {v['width']}x{v['height']} {dai:.1f}s")
    return ok


# --- video giả ---
# nói chuyện: dọc, tiếng "nói" 1,5s xen lặng 0,8s
ff('-f', 'lavfi', '-i', 'testsrc2=s=720x1280:r=30:d=12', '-f', 'lavfi', '-i',
   "aevalsrc='if(lt(mod(t,2.3),1.5),0.3*sin(2*PI*220*t),0)':s=48000:d=12", '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', f'{T}/noi.mp4')
# sản phẩm: ngang, không tiếng
ff('-f', 'lavfi', '-i', 'testsrc=s=1280x720:r=30:d=10', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', f'{T}/sp1.mov')
ff('-f', 'lavfi', '-i', 'smptebars=s=1920x1080:r=30:d=6', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', f'{T}/sp2.mp4')
# giọng đọc giả + nhạc có phách 120 BPM
ff('-f', 'lavfi', '-i', "aevalsrc='0.3*sin(2*PI*180*t)':s=48000:d=14", f'{T}/giong.mp3')
ff('-f', 'lavfi', '-i', "aevalsrc='0.8*sin(2*PI*60*t)*exp(-30*mod(t,0.5))+0.1*sin(2*PI*440*t)':s=48000:d=20", f'{T}/nhac.mp3')
ff('-f', 'lavfi', '-i', 'testsrc2=s=1024x1536', '-frames:v', '1', f'{T}/anh.png')   # ảnh minh hoạ giả để chèn
for i, c in enumerate(['red', 'blue', 'green', 'orange', 'purple', 'white']):
    ff('-f', 'lavfi', '-i', f'color=c={c}:s=1920x1080:r=30:d=4', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', f'{T}/v{i}.mp4')
th = os.path.join(T, 'thuong-hieu.json')
json.dump({'ten': 'Tiệm Nhà Mây', 'cau_ket': 'Bấm giỏ hàng để đặt ngay', 'mau_chinh': '#1B1B1B', 'mau_nhan': '#FFD21F'},
          open(th, 'w', encoding='utf-8'), ensure_ascii=False)
os.environ['AGENT_BOSS_HOME'] = os.path.join(T, 'nha')   # không đụng hồ sơ thật của người chạy thử
ok = True

# --- 1. phụ đề to ---
print('video-phu-de-to')
w = os.path.join(T, 'w1')
chay('video-phu-de-to', 'phan_tich.py', f'{T}/noi.mp4', '--ra', w, '--khong-nghe')
pt = os.path.join(w, 'phan-tich', 'noi.json')
d = json.load(open(pt, encoding='utf-8'))
cau = 'Hôm nay tôi chia sẻ ba sai lầm khi làm OKRs. Sai lầm đầu tiên là đặt quá nhiều mục tiêu, giảm 70% hiệu quả. Các bạn nhớ nhé'.split()
d['loi_noi'] = [[round(0.1 + (i // 4) * 2.3 + (i % 4) * 0.35, 2), round(0.4 + (i // 4) * 2.3 + (i % 4) * 0.35, 2), x] for i, x in enumerate(cau)]
json.dump(d, open(pt, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({'dau_ra': 'thanh-pham/video.mp4', 'thuong_hieu': '../thuong-hieu.json',
           'doan': [{'file': '../noi.mp4', 'tu': 4.6, 'den': 6.2}, {'file': '../noi.mp4', 'tu': 0, 'den': 12}],
           'chu': [{'tu': 0, 'den': 2.5, 'noi_dung': '3 SAI LẦM KHI LÀM OKRs', 'kieu': 'mo_dau'}],
           'tu_khoa': ['sai lầm', 'okrs'], 'sua_chu': {'okrs': 'OKRs'}, 'nhac': '../nhac.mp3',
           'chen_anh': [{'tu': 3, 'den': 6.5, 'anh': '../anh.png'}, {'tu': 7, 'den': 9, 'anh': '../anh.png', 'chuyen_dong': 'lia'}]},
          open(os.path.join(w, 'ke-hoach.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(chay('video-phu-de-to', 'dung.py', os.path.join(w, 'ke-hoach.json'), '--chi-thoi-gian'))
print(chay('video-phu-de-to', 'dung.py', os.path.join(w, 'ke-hoach.json')))
ok &= kiem(os.path.join(w, 'thanh-pham', 'video.mp4'), 11, 14)   # 12s gốc − ~2,6s lặng + 1,6s trích trước + 2,5s thẻ kết

# --- 2. mở hộp sản phẩm ---
print('video-mo-hop-san-pham')
w = os.path.join(T, 'w2')
chay('video-mo-hop-san-pham', 'phan_tich.py', f'{T}/sp1.mov', f'{T}/sp2.mp4', '--ra', w)
json.dump({'dau_ra': 'thanh-pham/video.mp4', 'thuong_hieu': '../thuong-hieu.json',
           'doan': [{'file': '../sp1.mov', 'tu': 1, 'den': 4}, {'file': '../sp2.mp4', 'tu': 0, 'den': 3},
                    {'file': '../sp1.mov', 'tu': 5, 'den': 9}, {'file': '../sp2.mp4', 'tu': 3, 'den': 6}],
           'chu': [{'tu': 0, 'den': 2.8, 'noi_dung': 'NHÀ CHẬT VẪN CHIÊN KHÔNG DẦU?', 'kieu': 'mo_dau'},
                   {'tu': 6, 'den': 9, 'noi_dung': '890K', 'kieu': 'gia'},
                   {'tu': 10, 'den': 'het', 'noi_dung': 'BẤM GIỎ HÀNG NGAY', 'kieu': 'cta'}],
           'giong_doc': {'file': '../giong.mp3'}, 'nhac': '../nhac.mp3'},
          open(os.path.join(w, 'ke-hoach.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(chay('video-mo-hop-san-pham', 'dung.py', os.path.join(w, 'ke-hoach.json')))
ok &= kiem(os.path.join(w, 'thanh-pham', 'video.mp4'), 15, 16)

# --- 3. ghép nhạc vlog ---
print('video-ghep-nhac-vlog')
w = os.path.join(T, 'w3')
json.dump({'dau_ra': 'thanh-pham/video.mp4', 'thuong_hieu': '../thuong-hieu.json',
           'doan': [{'file': f'../v{i}.mp4', 'tu': 0.5, 'den': 3.5} for i in range(6)],
           'chu': [{'tu': 0, 'den': 2.5, 'noi_dung': '1 NGÀY Ở ĐÀ LẠT', 'kieu': 'mo_dau'},
                   {'tu': 3, 'den': 5.5, 'noi_dung': 'sáng sớm sương mù', 'kieu': 'dan_chuyen'}],
           'nhac': '../nhac.mp3'}, open(os.path.join(w, 'ke-hoach.json'), 'w', encoding='utf-8') if os.makedirs(w, exist_ok=True) is None else None, ensure_ascii=False)
print(chay('video-ghep-nhac-vlog', 'dung.py', os.path.join(w, 'ke-hoach.json')))
ok &= kiem(os.path.join(w, 'thanh-pham', 'video.mp4'), 5, 16)

print(chay('video-phu-de-to', 'kiem_tra.py'))
print('TẤT CẢ OK' if ok else 'CÓ LỖI')
sys.exit(0 if ok else 1)
