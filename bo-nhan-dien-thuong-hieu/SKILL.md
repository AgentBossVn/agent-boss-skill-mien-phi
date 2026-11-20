---
name: bo-nhan-dien-thuong-hieu
description: "Dựng BỘ NHẬN DIỆN THƯƠNG HIỆU cho AI (brand guideline: màu, chữ, logo, luật dùng, 7 ấn phẩm mẫu, trang guideline) từ logo + web công ty, rồi làm ấn phẩm ĐÚNG thương hiệu: bài đăng, story, banner, slide, tài liệu A4, chữ ký email. Hay nói: 'làm brand guideline', 'bộ nhận diện công ty', 'thiết kế đúng thương hiệu', 'làm banner đúng màu công ty', 'AI thiết kế lệch màu brand'."
argument-hint: "[tên công ty + link web, hoặc: loại ấn phẩm + nội dung nếu đã có bộ]"
metadata:
  author: Mai Xuân Đạt — Agent Boss
  version: "1.0.0"
---

# Bộ nhận diện thương hiệu cho AI — dựng 1 lần, thiết kế đúng mãi

**Vì sao cần:** nhờ AI làm banner mà không đưa luật thương hiệu thì mỗi lần ra một kiểu: màu lệch, font lạ, logo bị vẽ lại, tiêu đề 5 cỡ chữ. Nhân viên mỗi người làm một phong cách. Skill này biến thương hiệu của bạn thành **bộ luật AI đọc được** (đã dùng thật cho Agent Boss và SEONGON), rồi mọi ấn phẩm sau đều làm theo bộ đó.

**Hai phần:**
- **Phần A — Dựng bộ (làm 1 lần, ~30–60 phút):** lấy màu thật từ logo + web, đo độ dễ đọc, viết luật, dựng 7 ấn phẩm mẫu + trang guideline. Bạn duyệt.
- **Phần B — Làm ấn phẩm (mỗi lần cần):** chép mẫu gần nhất, điền nội dung, chụp ảnh, tự soát theo luật, đưa bạn duyệt.

**Bước đầu tiên luôn là:** đọc `~/.agent-boss/thuong-hieu.json` (hồ sơ chung của các skill Agent Boss). Có khoá `bo_nhan_dien` và thư mục đó còn → **đã có bộ, sang Phần B**. Chưa có → Phần A.

## Vai của bạn và vai của Agent
| Câu hỏi | Trả lời |
|---|---|
| Ai quyết thương hiệu? | **Bạn.** Agent đo, đề xuất, ghi rõ chỗ nào đo được, chỗ nào là đề xuất. Bạn duyệt rồi mới thành luật |
| Công ty đã có brand book / quy chuẩn nhận diện? | Luật trong đó THẮNG. Agent chỉ chép lại cho AI đọc được, không tự đổi |
| Agent KHÔNG được làm | Tự vẽ hay sửa logo · thêm màu ngoài bộ · bịa số liệu, giải thưởng, tên khách · đưa sản phẩm chưa công bố vào ảnh gửi dịch vụ ngoài |
| Đo bằng gì? | Máy đo tương phản qua · ảnh mẫu không tràn chữ · Brand Test 3 câu · bạn nhìn thấy "đúng là công ty mình" |

## Chạy máy thế nào
`<SKILL>` = thư mục chứa tệp này. Máy chỉ cần Python 3.9+ có sẵn, không cài thêm thư viện. Chụp ảnh cần Chrome, Edge hoặc Brave (Windows luôn có Edge).
- Mac: `python3 <SKILL>/scripts/<máy>.py …`
- Windows: `py -3 <SKILL>/scripts/<máy>.py …` (KHÔNG gõ `python` trần: máy mới tinh đó là bản giả của Microsoft Store). Đường dẫn dùng `/`.

| Máy | Làm gì |
|---|---|
| `lay-mau.py <url \| logo.png \| logo.svg \| tệp.css>… [--json]` | Đếm màu dùng nhiều nhất (và font) từ web, logo |
| `do-tuong-phan.py "#hex" "#hex"` hoặc `do-tuong-phan.py <thư-mục-bộ>` | Đo độ dễ đọc chữ/nền theo chuẩn WCAG; bộ có cặp bắt buộc không đạt → báo lỗi |
| `dung-bo.py <thư-mục-bộ> [--chi-guideline] [--khong-ho-so]` | Từ `tokens.json` dựng 7 mẫu vào `mau/` + `guideline.html`, ghi hồ sơ chung `~/.agent-boss/thuong-hieu.json` |
| `chup-anh.py <tệp.html \| thư-mục> [--ra <thư-mục>]` | Chụp HTML thành PNG đúng khổ (khổ ghi ở thẻ `<meta name="kho">`) |

---

## Phần A — Dựng bộ nhận diện

### A1. Hỏi gọn trong 1 tin (có sẵn mặc định)
1. Tên công ty / thương hiệu, link web, fanpage. (bắt buộc)
2. **Tệp logo gốc** — tốt nhất SVG hoặc PNG nền trong suốt; có bản cho nền tối và nền sáng thì gửi cả hai. Chỉ có ảnh chụp/JPG → vẫn làm được, nhưng nói rõ logo sẽ kém nét và xin bạn hỏi người thiết kế cũ lấy tệp gốc.
3. Đã có brand book / quy chuẩn nhận diện chưa? Có → gửi (PDF, ảnh). 
4. 2–3 ấn phẩm cũ bạn ưng nhất, và 1–2 cái bạn ghét (để biết tránh gì).
5. Một câu nói công ty làm gì, cho ai. Các **con số / giải / khách tên tuổi được phép công bố** (chỉ những thứ này mới được lên ấn phẩm).
Thư mục làm việc: tạo `thuong-hieu-<tên-không-dấu>/` (cạnh nơi người dùng đang làm), logo chép vào `thuong-hieu-<tên>/logo/`.

### A2. Đo, không đoán
- Chạy `lay-mau.py` trên link web + từng tệp logo. Mở xem logo và ấn phẩm cũ bằng mắt (máy chỉ đếm điểm ảnh, không hiểu vai trò).
- Có brand book → đọc hết, lấy màu, font, luật ra **nguyên văn**; máy đo chỉ để kiểm brand book có khớp ấn phẩm thật không. Lệch → báo bạn, không tự chọn.
- Ghi lại mỗi giá trị lấy từ đâu (web / logo / brand book / Agent đề xuất). Phần "nguồn" này đi vào DESIGN.md.

### A3. Đề xuất bộ khung — 1 tin cho bạn duyệt
Dựng theo khung đã dùng cho Agent Boss và SEONGON:
- **Màu theo luật 80/15/5:** 1 màu **nền** chủ đạo (80% ấn phẩm), 1 màu **chữ** trên nền đó (15%), 1 màu **nhấn** dùng ≤5% (1 dòng tiêu đề, nút, chấm sơ đồ). Thêm: chữ phụ trên nền, màu thẻ nổi (đậm hơn nền một chút), nền sáng + chữ trên nền sáng (cho slide nội dung, tài liệu). Đủ 9 vai trong `tokens.json`. Không thêm màu thứ 4 "cho đẹp".
- Màu logo sáng quá làm nền (vàng, xanh mint…) → đề xuất màu đó làm **nhấn**, nền lấy màu đậm khác của thương hiệu; công ty chỉ có 1 màu → nền đậm trung tính (gần đen ấm hoặc xanh đen) + màu thương hiệu làm nhấn. Nói rõ đây là đề xuất.
- **Đo tương phản ngay:** `do-tuong-phan.py "#chữ" "#nền"` cho từng cặp. Cặp nào <4,5 thì chỉnh màu phụ (chữ phụ, chữ trên nút), KHÔNG chỉnh màu chính của logo. Màu nhấn trên nền chỉ đạt 3–4,5 → ghi luật "chữ nhấn tối thiểu 19px in đậm" (như SEONGON).
- **Font:** 1 họ font, có đủ dấu tiếng Việt, có trên Google Fonts (để ai cũng tải được): giữ font của web/brand book nếu có tiếng Việt; không có thì đề xuất Be Vietnam Pro / Inter / Montserrat / Roboto hợp tính cách. Kiểm dấu bằng cách dựng thử câu "Ưu đãi đặc biệt: Đặt lịch ở Đà Nẵng, Huế, Quảng Ngãi" rồi nhìn.
- **Hình đặc trưng** (như mũi tên SEONGON): 1 chi tiết lấy TỪ logo (biểu tượng, nét cong, hình khối) đặt ở vùng hình làm tâm bố cục. Agent chỉ cắt/tách từ tệp logo thật, không vẽ mới. Logo chỉ là chữ → để `null`, mẫu tự bỏ vùng hình.
- **Tiêu đề 3 tầng:** 3 dòng cùng cỡ, 1 dòng màu nhấn (chữ khoá: con số, tên chương trình), 2 dòng màu chữ; dưới là 1 câu phụ nhỏ hơn hẳn. Tối đa 3 cỡ chữ mỗi ấn phẩm.
- **Brand Test 3 câu** riêng của công ty (theo tính cách thương hiệu), ví dụ SEONGON: mắt đi một hướng? có bằng chứng thật? có hệ thống?

Tin duyệt gồm: bảng 9 màu (ô màu + hex + vai trò + nguồn + kết quả đo), font, hình đặc trưng, 3 câu Brand Test, những thứ CẤM (màu logo cũ, phong cách ghét). Hỏi 1 câu: "Bạn duyệt bộ khung này chưa, muốn đổi chỗ nào?".

### A4. Viết bộ (sau khi bạn duyệt)
Trong `thuong-hieu-<tên>/`:
- `logo/` — tệp thật: `logo-tren-nen.*` (dùng trên màu nền), `logo-tren-nen-sang.*`, `bieu-tuong-vuong.*` (ảnh đại diện), `hinh-dac-trung.*` (nếu có). Thiếu bản nào thì để `null` trong tokens.
- `tokens.json` — đúng mẫu ở [references/mau-tokens.json](references/mau-tokens.json).
- `DESIGN.md` — luật đầy đủ cho AI đọc, theo khung [references/mau-design.md](references/mau-design.md). Viết bằng lời của công ty, có ví dụ tiêu đề 3 tầng bằng nội dung thật của họ.
- `prompt.md` — bản ngắn ~60 dòng để chép-dán vào bất kỳ khung chat AI nào, theo [references/mau-prompt.md](references/mau-prompt.md).
Rồi: `do-tuong-phan.py thuong-hieu-<tên>` phải qua (mã thoát 0).

### A5. Dựng mẫu, chụp, tự soát
1. `dung-bo.py thuong-hieu-<tên>` → 7 mẫu trong `mau/` + `guideline.html`.
2. `chup-anh.py thuong-hieu-<tên>/mau` → ảnh trong `mau/xem-truoc/`.
3. **Mở xem TỪNG ảnh** (không chỉ tin máy): chữ tràn / đè hình, logo méo, thừa khoảng trống, dấu tiếng Việt lỗi, chữ nhấn quá nhiều. Sửa mẫu trong `mau/` (sửa bố cục, không đổi biến màu) → chụp lại. Muốn đổi màu/font → sửa `tokens.json` rồi chạy lại `dung-bo.py` (lệnh này GHI ĐÈ `mau/`: đổi màu trước, sửa bố cục sau).
4. `dung-bo.py thuong-hieu-<tên> --chi-guideline` để `guideline.html` lấy ảnh xem trước mà KHÔNG đụng `mau/` đã sửa tay.
   `dung-bo.py` báo hồ sơ chung `~/.agent-boss/thuong-hieu.json` không đọc được → nó đã dừng để khỏi xoá khoá của skill khác; mở tệp sửa lỗi JSON rồi chạy lại.
5. Đưa bạn: `guideline.html` (mở bằng trình duyệt) + 7 ảnh xem trước. Bạn góp ý → sửa → duyệt.

### A6. Dặn bạn cách dùng bộ ở chỗ khác
- Nhờ AI bất kỳ (ChatGPT, Gemini, Claude trên web): đính kèm `DESIGN.md` hoặc dán `prompt.md`, kèm tệp logo, rồi nói làm gì.
- Giao nhân viên / người thiết kế ngoài: gửi cả thư mục `thuong-hieu-<tên>/` (nén zip). Mẫu HTML mở bằng trình duyệt, sửa chữ là dùng.
- Các skill video của Agent Boss tự đọc màu + logo từ `~/.agent-boss/thuong-hieu.json` (máy `dung-bo.py` đã ghi), không phải nhập lại.

---

## Phần B — Làm ấn phẩm đúng thương hiệu

### B1. Đọc bộ, hỏi nội dung
Đọc `DESIGN.md` + `tokens.json` của bộ (đường dẫn ở khoá `bo_nhan_dien` trong hồ sơ chung). Hỏi gọn 1 tin: loại ấn phẩm + đăng ở đâu (mặc định theo bảng dưới), nội dung chữ, ảnh người thật / sản phẩm thật (nếu có). Số liệu, giải, tên khách: chỉ dùng thứ đã có trong DESIGN.md hoặc bạn đưa; thiếu thì hỏi, KHÔNG tự điền.

| Ấn phẩm | Mẫu gần nhất | Khổ |
|---|---|---|
| Bài đăng Facebook / Instagram | `bai-dang-4x5.html` | 1080×1350 |
| Story, Reels, TikTok ảnh | `story-9x16.html` | 1080×1920 |
| Banner sự kiện, ảnh link, ảnh bìa sự kiện | `banner-ngang.html` | 1200×630 |
| Slide bìa / slide nội dung | `slide-bia.html` / `slide-noi-dung.html` | 1920×1080 |
| Tài liệu, báo giá, thông báo in | `tai-lieu-a4.html` | A4 (794×1123) |
| Chữ ký email | `chu-ky-email.html` | 600×200 |

### B2. Làm
Chép mẫu gần nhất sang `an-pham/<ngày>-<tên-ngắn>/` (trong thư mục bộ), sửa CHỮ theo chú thích `SỬA CHỮ` đầu tệp. Không đổi biến màu, không thêm font. Khổ khác bảng → chép mẫu cùng hướng (ngang/dọc), đổi `<meta name="kho">` + kích thước, giữ bố cục trái chữ – phải hình (ngang) hoặc chữ trên – hình dưới (dọc). Ảnh người thật: khung tròn, viền màu nhấn 2px, như DESIGN.md.
Cần ảnh chụp minh hoạ có sản phẩm → dùng skill `anh-quang-cao-san-pham` (nếu đã cài) rồi đặt ảnh vào mẫu; cần video → skill video của Agent Boss.

### B3. Chụp và tự soát trước khi đưa bạn
`chup-anh.py an-pham/<…>/<tệp>.html` → mở xem ảnh. Soát đủ:
- [ ] Chỉ dùng màu trong `tokens.json`; màu nhấn ≤5% diện tích.
- [ ] ≤3 cỡ chữ; tiêu đề 3 tầng đúng luật; đọc được thông điệp chính trong 3 giây.
- [ ] Logo là tệp thật, đúng bản cho nền đó, không méo, không đặt trong hộp.
- [ ] Chữ không tràn, không đè hình; dấu tiếng Việt đúng; số ngăn nghìn bằng dấu chấm (`2.500+`).
- [ ] Không có số / giải / tên khách ngoài danh sách được phép.
- [ ] Qua đủ **Brand Test 3 câu** trong DESIGN.md. Sai 1 câu → làm lại.
Sửa tới khi qua hết, rồi mới đưa bạn ảnh PNG + tệp HTML (sửa chữ là dùng lại được).

### B4. Học từ góp ý
Bạn sửa cùng một kiểu từ 2 lần trở lên (vd "đừng để chữ nhấn 2 dòng") → đề xuất ghi thành luật mới vào DESIGN.md + prompt.md, nâng `phien_ban` trong tokens.json, ghi 1 dòng ở mục "Lịch sử" cuối DESIGN.md. Bạn đồng ý mới ghi.
