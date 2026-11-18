## Quy trình chung (mọi kiểu video)

Mọi lệnh chạy từ thư mục của skill này (thư mục chứa file SKILL.md). Gọi `<SKILL>` là đường dẫn thư mục đó.

### Bước 0. Kiểm tra (mỗi lần dùng)

Lệnh Python: macOS dùng `python3`, **Windows dùng `py -3`** (không gõ `python` trần: trên Windows mới đó là bản giả của Microsoft Store). Đường dẫn dùng `/`, chạy được cả Git Bash lẫn PowerShell. Dưới đây viết `python3`, trên Windows thay bằng `py -3`.

```bash
python3 <SKILL>/scripts/kiem_tra.py
```

- `thieu_bat_buoc` không rỗng → cho người dùng xem danh sách sẽ cài, hỏi **một câu** "Bạn đồng ý cài những thứ này không?", đồng ý rồi mới chạy. Cài ffmpeg xong trên Windows phải mở lại cửa sổ lệnh (hoặc khởi động lại Agent) để nhận lệnh `ffmpeg`.
- Thư viện Python **không** cài bằng `pip install --user` (macOS cài Python qua Homebrew sẽ từ chối). Lệnh `kiem_tra.py --cai` tự tạo Python riêng cho skill ở `~/.agent-boss/python` rồi cài vào đó; từ đó gõ `python3 <SKILL>/scripts/...` như thường, script tự chạy bằng Python riêng. Lệnh này cần Python 3.10–3.13 trên máy (bản mới hơn chưa chạy được thư viện nghe lời nói); không có thì nó in lệnh cài Python 3.12 (macOS: `brew install python@3.12`, Windows: `winget install -e --id Python.Python.3.12 --scope user`).
- `thieu_tuy_chon` → chỉ cài khi cần: `faster-whisper` cho phụ đề từ lời nói (lần đầu tự tải model ~1,5 GB, mất vài phút, chưa in gì ra là bình thường), `"opencv-python-headless<5"` để phụ đề tự né mặt người nói (nên cài với video quay cận mặt), `edge-tts` cho giọng đọc AI, `--cai-font` cho font Be Vietnam Pro (nên cài: không có thì chữ dùng Arial mảnh).
- `cap_nhat.co_ban_moi` là true → báo **một câu**: "Có bản mới {moi_nhat} của skill này. Cập nhật không?". Người dùng đồng ý thì làm đúng việc ghi ở `cau_cap_nhat`. **Không tự cập nhật.** `cap_nhat` là null thì bỏ qua, dựng bình thường.
- `cap_nhat.skill_khac_chua_cai` có tên → nhắc **một dòng** ở cuối câu trả lời: "Kho Agent Boss còn có: …". Chỉ nhắc một lần trong phiên.

### Bước 1. Hồ sơ thương hiệu (chỉ lần đầu)

Đọc `~/.agent-boss/thuong-hieu.json` (dùng chung cho mọi skill Agent Boss). Nếu chưa có, hỏi người dùng gọn trong **một** tin nhắn: tên shop/kênh, câu kêu gọi cuối video, màu chủ đạo, màu nhấn, đường dẫn logo (nếu có), file nhạc nền họ có quyền dùng (nếu có). Câu nào bỏ qua thì dùng mặc định. Ghi file:

```json
{"ten": "Tiệm Nhà Mây", "cau_ket": "Bấm giỏ hàng để đặt ngay", "mau_chinh": "#1B1B1B", "mau_nhan": "#FFD21F",
 "mau_chu": "#FFFFFF", "logo": "~/Pictures/logo.png", "font": null, "nhac": "~/Music/nen.mp3"}
```

File này nằm ngoài thư mục skill nên cập nhật skill không làm mất.

### Bước 2. Xem video đầu vào

```bash
python3 <SKILL>/scripts/phan_tich.py <video hoặc thư mục video> --ra <thư-mục-làm-việc>
```

Thư mục làm việc: tạo `video-<ngày>-<tên ngắn>/` cạnh video của người dùng. Với mỗi video, đọc `phan-tich/<tên>.json` (độ dài, khung dọc/ngang, chỗ lặng, chỗ đổi cảnh, lời nói từng chữ) và **mở xem ảnh** `phan-tich/<tên>.jpg` (lưới khung hình có ghi giây) để chọn đoạn đẹp. Video không có lời thì thêm `--khong-nghe` cho nhanh.

Phân tích còn ghi `mat` (vị trí mặt người nói mỗi giây, để phụ đề tự né mặt) và `vung_tieng` (có giá trị nghĩa là video gốc đổi tiếng giữa chừng, thường do điện thoại đổi micro hoặc bật lọc ồn: giọng đang ồm bỗng mỏng). Cả hai `dung.py` tự xử lý, không cần ghi gì vào kế hoạch.

Video dài thì máy in tiến độ "Đã nghe X/Y giây" mỗi phút. Máy tự bỏ khỏi phụ đề các câu máy nghe hay bịa ra ở đoạn lặng ("Hãy subscribe cho kênh…", "Cảm ơn các bạn đã theo dõi") và ghi lại từng câu đã bỏ; nếu người nói thật sự nói các câu đó thì chạy lại với `--khong-loc-bia`.

### Bước 3. Viết kế hoạch `ke-hoach.json` trong thư mục làm việc

```json
{
  "dau_ra": "thanh-pham/video.mp4",
  "doan": [{"file": "../clip1.mp4", "tu": 2.0, "den": 9.5}],
  "chu": [{"tu": 0, "den": 2.6, "noi_dung": "ĐỪNG MUA NỒI CHIÊN NẾU CHƯA XEM", "kieu": "mo_dau"}],
  "giong_doc": null,
  "sua_chu": {"cờ lốt": "Claude", "dịch ứng": "dị ứng"},
  "tu_khoa": ["giảm giá", "miễn phí"],
  "chen_anh": [{"tu": 8, "den": 12, "anh": "anh/1.jpg"}],
  "the_ket": true
}
```

- `doan`: giây trên video gốc, theo đúng thứ tự muốn xuất hiện. Đường dẫn tính từ thư mục chứa `ke-hoach.json`. Đặt `tu` đúng giờ chữ đầu câu trong `loi_noi` (lùi chừng 0,05 giây), đặt `den` ngay sau chữ cuối: đặt lệch là kéo theo nửa chữ của câu bên cạnh.
- `chu`: giây trên **video mới**. `"den": "het"` là tới cuối phần thân. `kieu` lấy theo bảng kiểu chữ của skill này.
- `giong_doc`: `{"van_ban": "...", "giong": "vi-VN-HoaiMyNeural"}` (nữ) hoặc `vi-VN-NamMinhNeural` (nam). Viết lời đọc như người nói chuyện, câu ngắn. Khoảng 3,5 chữ mỗi giây.
- `nhac`: đường dẫn nhạc người dùng đưa. Bỏ trống thì dùng nhạc trong hồ sơ thương hiệu; không có nữa thì kiểu video có lời (phụ đề to, mở hộp sản phẩm) **tự tạo nhạc nền** bằng code (không bản quyền, mỗi video một giai điệu). Video đã có nhạc sẵn hoặc người dùng không muốn nhạc thì để `"nhac": false`. **Chỉ dùng nhạc người dùng có quyền dùng**: không tự lấy nhạc trên mạng, không lấy nhạc của người khác trong máy.
- `sua_chu`: máy nghe sai chữ nào (tên riêng, tên sản phẩm, từ tiếng Anh) thì sửa ở đây. Đọc kỹ `van_ban` trong phân tích để bắt lỗi. Khoá viết đúng như máy nghe, được nhiều chữ; nên ghi cả cụm (`"dịch ứng"`) thay vì 1 chữ (`"dịch"`) để không sửa nhầm chỗ khác. Chữ sửa có chữ hoa ở giữa (`OKRs`, `iPhone`) giữ nguyên kiểu viết, còn lại (kể cả `Claude`) viết hoa như phụ đề.
- `chen_anh` (tuỳ chọn): ảnh minh hoạ phủ kín khung trong lúc lời nói vẫn chạy, có chuyển động chậm (`"chuyen_dong"`: `zoom_in`, `zoom_out` hoặc `lia`; bỏ trống thì tự xoay vòng). `tu`/`den` là giây trên video mới (xem bằng `--chi-thoi-gian`), mỗi ảnh 3–7 giây, đặt đúng lúc người nói kể chuyện có hình dung được. Ảnh dọc 9:16 là đẹp nhất. **Chỉ dùng ảnh người dùng có quyền dùng** (ảnh của họ, ảnh họ tự tạo bằng AI).
- `vi_tri_phu_de` (tuỳ chọn): đặt cứng vị trí phụ đề theo chiều cao, 0–1, không đặt số lớn hơn `0.78` (sát đáy sẽ đè tên kênh, chú thích của TikTok). Thường không cần: đã cài OpenCV thì phụ đề tự né mặt (xuống dưới cằm, không đủ chỗ thì lên trên đầu, vẫn chật thì thu nhỏ chữ).

Muốn biết giờ từng cụm phụ đề trên video mới (để đặt chữ cho khớp lời): `python3 <SKILL>/scripts/dung.py ke-hoach.json --chi-thoi-gian`.

### Bước 4. Dựng

```bash
python3 <SKILL>/scripts/dung.py <thư-mục-làm-việc>/ke-hoach.json
```

Ra `thanh-pham/video.mp4` (1080×1920, 30 hình/giây, tiếng chuẩn −14 LUFS) và `thanh-pham/video-bia.jpg`.

### Bước 5. Tự soát rồi giao

1. Trích 3 khung hình (đầu, giữa, cuối) bằng ffmpeg và **xem**: chữ có tràn mép, che mặt, sai dấu không. Có lỗi thì sửa kế hoạch và dựng lại.
2. Viết `thanh-pham/chu-thich.txt`: 1 câu mở đầu gây tò mò + 2–3 dòng nội dung + lời kêu gọi + 4–6 hashtag tiếng Việt sát chủ đề (không nhồi hashtag chung chung).
3. Làm bản khoe "trước – sau" (video gốc và thành phẩm chạy cạnh nhau 10 giây, đăng hoặc gửi khoe được ngay): `python3 <SKILL>/scripts/truoc_sau.py <thư-mục-làm-việc>/ke-hoach.json` → `thanh-pham/video-truoc-sau.mp4`.
4. Báo người dùng: đường dẫn video, bản trước – sau, ảnh bìa, chú thích. Hỏi có muốn sửa gì không (đổi câu mở đầu, ngắn hơn, đổi nhạc).

### Luật chung

- Video dọc 9:16. Chữ trong vùng an toàn của TikTok: không sát mép phải (cột nút bấm), không thấp quá 80% chiều cao (chỗ tên kênh, chú thích).
- 3 giây đầu quyết định người xem có ở lại. Luôn có câu mở đầu rõ ràng.
- Không hứa hẹn sai sự thật, không dùng "cam kết 100%", "chữa khỏi", "tốt nhất" cho mỹ phẩm, thực phẩm chức năng, thuốc (dễ bị TikTok bóp hoặc từ chối quảng cáo).
- Không dùng nhạc, hình, logo người dùng không có quyền dùng.
