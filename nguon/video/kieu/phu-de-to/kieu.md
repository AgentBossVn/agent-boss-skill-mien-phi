---
name: video-phu-de-to
description: Dựng video nói chuyện/chia sẻ (người nói trước camera, podcast, livestream) thành video TikTok/Reels/Shorts dọc đăng được ngay — cắt hết chỗ lặng và ấp úng, phụ đề tiếng Việt chữ to giữa khung tô màu từ khoá, đổi khung phóng to/thu nhỏ giữ nhịp, câu đắt nhất đưa lên đầu, nhạc nền nhỏ, thẻ kết thương hiệu. Dùng khi người dùng có video tự quay đang nói và muốn "edit lại đăng TikTok", "làm phụ đề", "cắt cho gọn".
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
6. **Ảnh minh hoạ chèn xen:** video chỉ có mặt người nói từ đầu tới cuối rất dễ bị lướt qua. Mỗi 10–20 giây chèn 1 ảnh (`chen_anh`) minh hoạ đúng chuyện đang kể, 3–7 giây mỗi ảnh. Không có ảnh thì hỏi người dùng có muốn tạo không, đừng tự bịa ảnh không khớp lời.
7. **Nhạc:** nhẹ, lót suốt video dưới giọng nói. Nên có: video chỉ có giọng nói nghe trống. Không có nhạc có quyền dùng thì để trống.
8. **Thẻ kết:** bật (`"the_ket": true`) — tên kênh + câu kêu gọi từ hồ sơ thương hiệu.

## Kiểu chữ có trong skill này

| kieu | Dùng cho | Vị trí |
|---|---|---|
| `mo_dau` | Câu mở đầu 3 giây đầu | Trên cao, chữ trắng viền đen |
| `nhan` | Tiêu đề chuyển ý | Trên cao, nền màu nhấn |

