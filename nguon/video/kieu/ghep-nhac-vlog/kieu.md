---
name: video-ghep-nhac-vlog
description: Ghép các clip đời sống, du lịch, ăn uống, một ngày làm việc (không cần lời nói) thành video TikTok/Reels dọc cắt khớp nhịp nhạc, đăng được ngay — tự chọn cảnh đẹp, mỗi cảnh đổi đúng phách nhạc, chữ dẫn chuyện ngắn. Dùng khi người dùng có nhiều clip quay cảnh và muốn "ghép thành video", "làm vlog", "video theo nhạc".
---

# Video ghép nhạc / vlog

**Hợp với:** clip cảnh đời sống, du lịch, đồ ăn, không gian quán, hậu trường, "một ngày của tôi".
**Không hợp với:** video có người nói quan trọng (dùng `video-phu-de-to`).

## Công thức (10–30 giây)

1. **Nhạc là bắt buộc:** cần file nhạc người dùng có quyền dùng (hồ sơ thương hiệu hoặc hỏi). Nhạc có nhịp rõ thì cắt khớp đẹp hơn. Không có nhạc → báo người dùng, gợi ý họ lấy nhạc từ thư viện miễn phí bản quyền hoặc thêm nhạc trong app TikTok sau khi đăng (khi đó dựng không nhạc, cảnh dài 1,5–2 giây đều nhau).
2. **Chọn cảnh:** 8–15 đoạn, mỗi đoạn lấy phần đẹp nhất dài ~3 giây (skill tự cắt cho khớp phách, cảnh từ 0,8 đến 2,6 giây). Cảnh đẹp/ấn tượng nhất lên đầu; xen cảnh rộng – cận; cảnh cuối là cảnh "kết" (hoàng hôn, nụ cười, món ăn hoàn chỉnh).
3. **Chữ:** `mo_dau` 0–2,5 giây là tiêu đề ngắn ("1 NGÀY Ở ĐÀ LẠT", "QUÁN NHỎ GIỮA PHỐ"). `dan_chuyen` cho 2–4 câu dẫn chuyện nhỏ, mỗi câu 2–3 giây, chữ thường cảm xúc. Ít chữ thôi, để hình nói.
4. **Tiếng gốc:** tắt. Thẻ kết: tắt (vlog kết bằng cảnh đẹp hơn thẻ).

## Kiểu chữ có trong skill này

| kieu | Dùng cho | Vị trí |
|---|---|---|
| `mo_dau` | Tiêu đề | Giữa khung, chữ to |
| `dan_chuyen` | Câu dẫn chuyện | Dưới, chữ nhỏ |


## Tự động theo preset
- Mỗi cảnh mở đầu bằng cú phóng nhẹ, cứ cảnh thứ 4 loé trắng 2 khung; `"mau_sac": "am"` trong preset = tông màu ấm nhẹ (bỏ dòng đó nếu muốn màu gốc).
