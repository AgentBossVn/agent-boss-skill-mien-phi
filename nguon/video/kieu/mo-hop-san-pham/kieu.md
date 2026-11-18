---
name: video-mo-hop-san-pham
description: Biến video quay sản phẩm (mở hộp, cận cảnh, dùng thử — có hoặc không có lời) thành video bán hàng TikTok Shop/Shopee Video/Reels dọc đăng được ngay — chọn cảnh đẹp nhất, nhịp nhanh, giọng đọc AI tiếng Việt, phụ đề kiểu karaoke, chữ giá to, lời kêu gọi bấm giỏ hàng, thẻ kết thương hiệu. Dùng khi người dùng có clip sản phẩm và muốn "làm video bán hàng", "video affiliate", "video giỏ hàng".
---

# Video mở hộp / sản phẩm

**Hợp với:** clip quay sản phẩm, mở hộp, dùng thử, quay hàng ở shop. Không cần người nói — skill tự viết lời và đọc bằng giọng AI.
**Không hợp với:** video người nói chuyện dài (dùng `video-phu-de-to`).

## Công thức (15–30 giây, bán hàng)

1. **Hỏi người dùng (một tin nhắn, nếu chưa nói):** tên sản phẩm, giá (và giá gốc nếu đang giảm), 2–3 điểm mạnh, ai nên mua, lời kêu gọi (giỏ hàng / inbox / link bio).
2. **Chọn cảnh:** xem ảnh lưới phân tích, chọn 5–9 đoạn 1,5–3 giây: cảnh đẹp nhất lên đầu, sau đó chi tiết, dùng thử, kết quả. Bỏ cảnh mờ, rung, tay che. Tổng thân video khớp với độ dài lời đọc.
3. **Lời đọc (`giong_doc`) theo khung 4 nhịp:**
   - *Móc (0–3 giây):* chạm nỗi đau hoặc gây tò mò. "Nhà chật mà vẫn muốn chiên không dầu?"
   - *Giới thiệu:* sản phẩm là gì, 1 câu.
   - *2–3 lợi ích cụ thể:* có số liệu nếu có ("5 lít", "chỉ 15 phút").
   - *Chốt:* giá + lời kêu gọi. "Giá chỉ 890 nghìn, bấm giỏ hàng góc trái ngay nhé."
   - 50–90 chữ cho 15–25 giây. Văn nói tự nhiên, không liệt kê thông số khô.
4. **Chữ trên hình:** `mo_dau` 0–2,8 giây (≤ 7 chữ); `gia` khi lời đọc nhắc giá (ví dụ "890K"); `cta` 3 giây cuối thân ("BẤM GIỎ HÀNG 🛒" — không dùng emoji nếu font không hỗ trợ).
5. **Video vào là khung ngang:** tự đặt lên nền mờ, không cắt mất sản phẩm.
6. **Tiếng gốc:** tắt (giọng AI thay). Nếu tiếng gốc có giá trị (tiếng xèo xèo, tiếng mở hộp) thì vẫn tắt ở bản đầu, hỏi người dùng sau.
7. **Không có edge-tts / không có mạng:** bỏ `giong_doc`, chỉ dùng chữ trên hình + nhạc (thêm nhiều chữ `nhan` cho từng lợi ích).

## Kiểu chữ có trong skill này

| kieu | Dùng cho | Vị trí |
|---|---|---|
| `mo_dau` | Câu móc 3 giây đầu | Trên cao, chữ trắng viền đậm, hơi nghiêng |
| `gia` | Giá, % giảm | Giữa khung, nền màu nhấn, chữ rất to |
| `nhan` | Lợi ích ngắn ("5 LÍT", "CHỐNG DÍNH") | Trên cao, nền màu chính |
| `cta` | Lời kêu gọi cuối | Dưới giữa, nền màu nhấn |


## Khoá tuỳ chọn trong kế hoạch
- Chữ `mo_dau` tự hiện từng chữ một (chữ trong `tu_khoa` tô màu nhấn và bật nảy); `"hien_dan": false` để tắt. `"phat_sang": ["ĐẶT TRƯỚC"]`: phụ đề chứa cụm đó có quầng sáng + sao (tối đa 2 cụm).
