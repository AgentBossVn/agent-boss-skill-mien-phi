# Khung DESIGN.md — luật thương hiệu đầy đủ cho AI đọc

Agent điền khung dưới đây bằng nội dung THẬT của công ty, bỏ mọi chữ trong `[...]`. Viết ngắn, mệnh lệnh rõ (NÊN / KHÔNG / CẤM), có ví dụ cụ thể. Mỗi giá trị đo được ghi nguồn. Ví dụ đã chạy thật: bộ SEONGON (nền xanh `#004AEF`, nhấn mint `#07EF9C`, hình đặc trưng = mũi tên trong logo).

````markdown
---
version: 1.0
name: [TÊN THƯƠNG HIỆU]
description: [Câu định vị]. Bộ nhận diện dùng cho mọi ấn phẩm [TÊN].
nguon: [logo lấy từ tệp …; màu đo từ web … và logo bằng lay-mau.py ngày …; brand book … (nếu có)]
---

# [TÊN] — Bộ nhận diện (bản 1.0)

## 1. Tính cách thương hiệu
**Câu định vị:** *[…]*
Cảm xúc cần ra: **[3–4 từ]** (vd: Đáng tin · Gần gũi · Có số chứng minh).
3 nguyên tắc:
1. **[Tên]** — [1 câu, vd: mỗi ấn phẩm 1 thông điệp chính].
2. **[Tên]** — [vd: bằng chứng thật: số, khách, người thật; không hình AI sáo rỗng].
3. **[Tên]** — […].

## 2. Màu — luật 80/15/5
| Tỉ lệ | Màu | Vai trò |
|---|---|---|
| 80% | [tên] `#……` | Nền. Phẳng, không chuyển màu |
| 15% | [tên] `#……` | Chữ chính trên nền |
| ≤5% | [tên] `#……` | Nhấn: 1 dòng tiêu đề, nút, chấm sơ đồ |
Phụ: `#……` thẻ nổi · `#……` chữ phụ trên nền · nền sáng `#……` + chữ `#……` / `#……`.
**Tương phản (đo bằng do-tuong-phan.py):** [ghi từng luật rút ra, vd: chữ nhấn trên nền 4,29:1 → chỉ dùng từ 19px in đậm; nút nhấn dùng chữ `#……`; KHÔNG dùng chữ nhấn trên nền sáng].
**CẤM:** [màu logo cũ, màu đối thủ, nền chuyển màu kiểu kính, khối 3D…].

## 3. Chữ
- Một font: **[Tên]** (Google Fonts). Tiêu đề [700], chữ thường 400–500.
- **Tiêu đề 3 tầng** (banner, bài đăng, bìa): 3 dòng cùng cỡ, 1 dòng màu nhấn (chữ khoá), 2 dòng màu chữ; dưới là 1 câu phụ nhỏ hơn hẳn. Ví dụ bằng nội dung thật:
  ```
  [DÒNG NHẤN]      ← màu nhấn
  [DÒNG 2]         ← màu chữ
  [DÒNG 3]         ← màu chữ
  [Câu phụ]        ← chữ phụ
  ```
- Tối đa 3 cỡ chữ mỗi ấn phẩm. Số ngăn nghìn bằng dấu chấm (`2.500+`). Dòng thông tin: `giờ · thứ, ngày · hình thức`, dấu `·` màu nhấn.

## 4. Logo — dùng TỆP THẬT, không vẽ lại
- Trên nền màu: `logo/…` · Trên nền sáng: `logo/…` · Biểu tượng vuông: `logo/…`.
- Khoảng trống quanh logo ≥ [chiều cao 1 chữ cái của logo]. Cỡ nhỏ nhất: rộng [120px] màn hình.
- KHÔNG đặt trong hộp, đổi màu, thêm bóng/viền, kéo méo. [Logo cũ … đã bỏ.]

## 5. Hình đặc trưng
[Tên hình — lấy từ chi tiết nào của logo. Đặt ở vùng hình, làm tâm bố cục; không xoay, không đổi màu, không cắt. Quanh nó 3–5 nút việc (chấm màu nhấn + nhãn) nếu cần sơ đồ. 1 quầng màu nhấn rất mờ phía sau, KHÔNG sau chữ.]
[Không có hình đặc trưng → ghi: "Không dùng hình trang trí; vùng hình để ảnh người thật / sản phẩm thật".]

## 6. Bố cục
- **Khổ ngang:** chữ trái ~55% (logo → nhãn → tiêu đề 3 tầng → câu phụ → thông tin), hình phải ~45%.
- **Khổ dọc:** chữ trên, hình dưới. Story chừa 250px trên và dưới.
- **Nền sáng** (slide nội dung, A4): nền sáng 80%, màu chính cho tiêu đề, logo bản nền sáng góc phải.
- **3 lớp:** nền phẳng → hình đặc trưng + quầng → người thật + chữ (rõ nhất).
- Ảnh người thật: khung tròn, viền màu nhấn 2px, tên in đậm, chức danh chữ phụ.

## 7. Nên / Không nên
| ✅ Nên | ❌ Không nên |
|---|---|
| […] | […] |
(4–6 dòng, rút từ ấn phẩm cũ người dùng ưng / ghét)

## 8. Bằng chứng được dùng
Chỉ dùng số, giải, khách đã công bố dưới đây; cần số khác → hỏi [ai], KHÔNG tự đoán.
- […]

## 9. Khổ ấn phẩm thường dùng
| Ấn phẩm | Khổ | Mẫu |
|---|---|---|
| Bài đăng 4:5 | 1080×1350 | `mau/bai-dang-4x5.html` |
| Story 9:16 | 1080×1920 | `mau/story-9x16.html` |
| Banner ngang | 1200×630 | `mau/banner-ngang.html` |
| Slide bìa / nội dung | 1920×1080 | `mau/slide-bia.html` / `mau/slide-noi-dung.html` |
| Tài liệu A4 | 794×1123 | `mau/tai-lieu-a4.html` |
| Chữ ký email | 600×200 | `mau/chu-ky-email.html` |

## 🧪 Brand Test — trả lời ĐÚNG cả 3 câu trước khi giao
| # | Câu hỏi |
|---|---|
| 1 | [vd: Mắt người xem có đi một hướng không — 1 thông điệp, đọc trong 3 giây?] |
| 2 | [vd: Có bằng chứng thật không — số / người thật / khách?] |
| 3 | [câu riêng theo tính cách thương hiệu] |
Sai 1 câu → làm lại.

## Lịch sử
- 1.0 ([dd/mm/yyyy]) — bản đầu.
````
