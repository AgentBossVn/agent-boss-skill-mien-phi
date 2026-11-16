---
name: video-phu-de-to
description: Dựng video nói chuyện/chia sẻ (người nói trước camera, podcast, livestream) thành video TikTok/Reels/Shorts dọc đăng được ngay — cắt hết chỗ lặng và ấp úng, phụ đề tiếng Việt chữ to giữa khung tô màu từ khoá, đổi khung phóng to/thu nhỏ giữ nhịp, câu đắt nhất đưa lên đầu, nhạc nền nhỏ, thẻ kết thương hiệu. Dùng khi người dùng có video tự quay đang nói và muốn "edit lại đăng TikTok", "làm phụ đề", "cắt cho gọn".
metadata:
  author: Mai Xuân Đạt — Agent Boss
  version: "1.0.0"
---

# Video phụ đề to (nói chuyện, chia sẻ)

**Hợp với:** người nói trước camera, chia sẻ kinh nghiệm, bài giảng ngắn, cắt từ podcast hoặc livestream.
**Không hợp với:** video không có lời (dùng `video-ghep-nhac-vlog`), video sản phẩm cận cảnh (dùng `video-mo-hop-san-pham`).

## Công thức

1. **Độ dài:** 30–90 giây. Video gốc dài hơn thì chọn **một ý trọn vẹn** đắt nhất (đọc `van_ban` trong phân tích), không cắt vụn nhiều ý.
2. **Câu mở đầu (3 giây đầu):** tìm câu gây tò mò hoặc gây sốc nhất trong lời nói. Đặt nó làm đoạn **đầu tiên** trong `doan` (trích trước), rồi mới đến thân bài theo thứ tự. Đồng thời thêm chữ `mo_dau` 0–2,6 giây: câu hỏi hoặc lời hứa ngắn ≤ 8 chữ, viết hoa.
3. **Cắt lặng:** tự động (bỏ khoảng lặng > 0,3 giây). Thêm vào `sua_chu` mọi chữ máy nghe sai, đặc biệt tên riêng và từ tiếng Anh.
4. **Từ khoá:** chọn 5–10 từ/cụm đắt (con số, kết quả, nỗi đau) cho `tu_khoa`: phụ đề sẽ tô màu nhấn; cụm ≤ 2 chữ có từ khoá hiện to và nghiêng.
5. **Chữ nhấn giữa video (tuỳ chọn):** kiểu `nhan` cho tiêu đề phụ khi chuyển ý ("BƯỚC 2", "SAI LẦM SỐ 1").
6. **Nhạc:** nhẹ, nằm dưới giọng nói. Không có nhạc thì để trống, vẫn ổn.
7. **Thẻ kết:** bật (`"the_ket": true`) — tên kênh + câu kêu gọi từ hồ sơ thương hiệu.

## Kiểu chữ có trong skill này

| kieu | Dùng cho | Vị trí |
|---|---|---|
| `mo_dau` | Câu mở đầu 3 giây đầu | Trên cao, chữ trắng viền đen |
| `nhan` | Tiêu đề chuyển ý | Trên cao, nền màu nhấn |

## Quy trình chung (mọi kiểu video)

Mọi lệnh chạy từ thư mục của skill này (thư mục chứa file SKILL.md). Gọi `<SKILL>` là đường dẫn thư mục đó.

### Bước 0. Kiểm tra (mỗi lần dùng)

Lệnh Python: macOS dùng `python3`, **Windows dùng `py -3`** (không gõ `python` trần: trên Windows mới đó là bản giả của Microsoft Store). Đường dẫn dùng `/`, chạy được cả Git Bash lẫn PowerShell. Dưới đây viết `python3`, trên Windows thay bằng `py -3`.

```bash
python3 <SKILL>/scripts/kiem_tra.py
```

- `thieu_bat_buoc` không rỗng → cho người dùng xem danh sách sẽ cài, hỏi **một câu** "Bạn đồng ý cài những thứ này không?", đồng ý rồi mới chạy. Windows chưa có Python: `winget install -e --id Python.Python.3.12 --scope user`. Cài ffmpeg xong trên Windows phải mở lại cửa sổ lệnh (hoặc khởi động lại Agent) để nhận lệnh `ffmpeg`.
- `thieu_tuy_chon` → chỉ cài khi cần: `faster-whisper` cho phụ đề từ lời nói (lần đầu tự tải model ~800 MB), `edge-tts` cho giọng đọc AI.
- `cap_nhat.co_ban_moi` là true → báo **một câu**: "Có bản mới {moi_nhat} của skill này. Cập nhật không?". Người dùng đồng ý thì làm đúng việc ghi ở `cau_cap_nhat`. **Không tự cập nhật.** `cap_nhat` là null thì bỏ qua, dựng bình thường.
- `cap_nhat.skill_khac_chua_cai` có tên → nhắc **một dòng** ở cuối câu trả lời: "Kho Agent Boss còn có: …". Chỉ nhắc một lần trong phiên.
- Font: nếu chữ lỗi dấu hoặc trông xấu, chạy `python3 <SKILL>/scripts/kiem_tra.py --cai-font` (tải Be Vietnam Pro từ Google Fonts).

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

### Bước 3. Viết kế hoạch `ke-hoach.json` trong thư mục làm việc

```json
{
  "dau_ra": "thanh-pham/video.mp4",
  "doan": [{"file": "../clip1.mp4", "tu": 2.0, "den": 9.5}],
  "chu": [{"tu": 0, "den": 2.6, "noi_dung": "ĐỪNG MUA NỒI CHIÊN NẾU CHƯA XEM", "kieu": "mo_dau"}],
  "giong_doc": null,
  "nhac": null,
  "sua_chu": {"cờ lốt": "Claude"},
  "tu_khoa": ["giảm giá", "miễn phí"],
  "the_ket": true
}
```

- `doan`: giây trên video gốc, theo đúng thứ tự muốn xuất hiện. Đường dẫn tính từ thư mục chứa `ke-hoach.json`.
- `chu`: giây trên **video mới**. `"den": "het"` là tới cuối phần thân. `kieu` lấy theo bảng kiểu chữ của skill này.
- `giong_doc`: `{"van_ban": "...", "giong": "vi-VN-HoaiMyNeural"}` (nữ) hoặc `vi-VN-NamMinhNeural` (nam). Viết lời đọc như người nói chuyện, câu ngắn. Khoảng 3,5 chữ mỗi giây.
- `nhac`: bỏ trống thì dùng nhạc trong hồ sơ thương hiệu; không có thì không lót nhạc. **Chỉ dùng nhạc người dùng có quyền dùng.** Video đã có nhạc sẵn thì để `"nhac": null`.
- `sua_chu`: máy nghe sai chữ nào (tên riêng, tên sản phẩm, từ tiếng Anh) thì sửa ở đây. Đọc kỹ `van_ban` trong phân tích để bắt lỗi.

Muốn biết giờ từng cụm phụ đề trên video mới (để đặt chữ cho khớp lời): `python3 <SKILL>/scripts/dung.py ke-hoach.json --chi-thoi-gian`.

### Bước 4. Dựng

```bash
python3 <SKILL>/scripts/dung.py <thư-mục-làm-việc>/ke-hoach.json
```

Ra `thanh-pham/video.mp4` (1080×1920, 30 hình/giây, tiếng chuẩn −14 LUFS) và `thanh-pham/video-bia.jpg`.

### Bước 5. Tự soát rồi giao

1. Trích 3 khung hình (đầu, giữa, cuối) bằng ffmpeg và **xem**: chữ có tràn mép, che mặt, sai dấu không. Có lỗi thì sửa kế hoạch và dựng lại.
2. Viết `thanh-pham/chu-thich.txt`: 1 câu mở đầu gây tò mò + 2–3 dòng nội dung + lời kêu gọi + 4–6 hashtag tiếng Việt sát chủ đề (không nhồi hashtag chung chung).
3. Báo người dùng: đường dẫn video, ảnh bìa, chú thích. Hỏi có muốn sửa gì không (đổi câu mở đầu, ngắn hơn, đổi nhạc).

### Luật chung

- Video dọc 9:16. Chữ trong vùng an toàn của TikTok: không sát mép phải (cột nút bấm), không thấp quá 80% chiều cao (chỗ tên kênh, chú thích).
- 3 giây đầu quyết định người xem có ở lại. Luôn có câu mở đầu rõ ràng.
- Không hứa hẹn sai sự thật, không dùng "cam kết 100%", "chữa khỏi", "tốt nhất" cho mỹ phẩm, thực phẩm chức năng, thuốc (dễ bị TikTok bóp hoặc từ chối quảng cáo).
- Không dùng nhạc, hình, logo người dùng không có quyền dùng.
