---
name: anh-quang-cao-san-pham
description: "Ảnh quảng cáo có SẢN PHẨM THẬT đúng nhãn như ảnh hãng: vẽ bằng gói AI đang trả (ChatGPT, Gemini; Claude dựng bằng code) rồi mới tới API, công cụ chuyên nghiệp; máy đọc chữ soát nhãn, dán nhãn thật, đặt chữ, đóng vai khách xem lại. Hay nói: 'làm ảnh quảng cáo sản phẩm X', 'ảnh ads sai chi tiết'."
argument-hint: "[sản phẩm + link web hãng, vd: nồi chiên không dầu hãng X + link trang sản phẩm]"
metadata:
  author: Mai Xuân Đạt — Agent Boss
  version: "3.0.0"
---

# Ảnh quảng cáo có sản phẩm thật — đúng chi tiết, đẹp như ảnh mẫu

**Vì sao cần skill này:** AI vẽ cảnh rất đẹp nhưng CÓ THỂ vẽ sai sản phẩm thật: thừa đèn, thiếu nút, logo méo, chữ trên nhãn thành chữ lạ, "336 g" thành "136 g". Khách của hãng nhìn ra ngay. Người bán hàng cần ảnh vừa đẹp vừa ĐÚNG.

**Dùng skill này hơn gì so với tự gõ trong khung chat:** Trên máy bạn, Agent sẽ tự làm từ đầu đến cuối: tải ảnh hãng về đếm từng chi tiết rồi mới vẽ, **dùng công cụ đọc chữ để đối chiếu nhãn trên ảnh vẽ với ảnh hãng**, cắt phóng to để soát từng vùng, chỗ nào AI vẽ sai thì lấy nhãn THẬT của hãng dán đè lên, dàn chữ lên ảnh, rồi **tự đóng vai khách hàng của bạn lướt xem ảnh** để sửa tiếp, xong xuôi mới đưa bạn duyệt. Bạn vẫn là người duyệt cuối.

**Agent nào tự vẽ được ảnh (kiểm tra ngày 15/11/2026):** Agent của ChatGPT (Codex) và của Gemini (Antigravity) có sẵn công cụ vẽ. **Claude KHÔNG vẽ được ảnh** (trang trợ giúp Anthropic): Claude tự làm bằng cách cắt sản phẩm thật từ ảnh hãng, dựng nền + chữ bằng code; muốn có cảnh chụp thì Claude phải gọi sang gói ChatGPT hoặc Gemini sẵn có trên máy bạn để vẽ hộ.
**Bạn là Agent đang chạy skill này trong Codex hoặc Antigravity** → vẽ thẳng bằng công cụ vẽ có sẵn của mình (Codex: `image_gen` / `$imagegen`; Antigravity: `generate_image`), đưa ảnh hãng vào làm ảnh mẫu, lưu ảnh vẽ xong vào thư mục `ve/`, còn mọi bước khác giữ nguyên.

## Vai của bạn và vai của Agent
| Câu hỏi | Trả lời mặc định |
|---|---|
| Ảnh phục vụ mục tiêu gì? | Bán được hàng: đúng sản phẩm, đúng thông điệp, đăng được ngay |
| Ai chịu trách nhiệm cuối? | **Bạn** — duyệt thông điệp, chọn ảnh, bấm đăng |
| Agent được tự quyết tới đâu? | Chọn bản vẽ, sửa chi tiết, bỏ ảnh hỏng. KHÔNG tự đổi thông điệp, KHÔNG tự chuyển sang đường trả tiền, KHÔNG tiêu quá trần |
| Đo bằng gì? | Qua 100% danh sách soát + máy đọc chữ + bạn ưng khi đặt cạnh ảnh hãng |
| Agent sai thì sao? | Bạn chỉ rõ vùng sai (khoanh / mô tả) → Agent sửa vùng đó, soát lại |

## Bước 0 — Hỏi ngắn (gộp 1 tin, có sẵn đáp án mặc định)
1. Sản phẩm nào, link trang hãng / gian hàng chính hãng? (bắt buộc)
2. Có ảnh mẫu bạn ưng không? Gửi vào thư mục làm việc.
3. Đăng ở đâu, bao nhiêu ảnh? Mặc định Facebook: 1 dọc 4:5 (1080×1350) + 1 ngang 16:9 (1920×1080) + 1 story 9:16 (1080×1920).
   Bán cho ai? Chưa nói → Agent tự suy từ trang hãng, ghi 1 dòng chân dung khách (ai, tuổi, đang lo gì khi mua) để bạn sửa — dùng ở Bước 7b.
4. Thông điệp / chữ muốn đặt? Chưa có → Agent đề xuất từ sự thật trên trang hãng, bạn duyệt trước khi đặt.
5. **Chọn công cụ vẽ: người dùng chọn, Agent lo cài.** Chạy `python3 scripts/kiem-cong-cu-ve.py`, đưa NGUYÊN bảng nó in (xếp sẵn theo thứ tự nên dùng) kèm 1 câu gợi ý, rồi hỏi: "Bạn muốn vẽ bằng công cụ nào?". KHÔNG mặc định đường trả tiền, KHÔNG bắt ai phải trả thêm.
   Chọn công cụ chưa sẵn sàng → Agent TỰ chạy hết các dòng "Agent chạy" máy kiểm in ra (lệnh mở trình duyệt / chờ người bấm thì chạy nền), chỉ dừng chờ ở dòng "Bạn làm" (bấm đăng nhập / cho phép, gõ mật khẩu máy, bấm Cài đặt, dán khoá vào ô kín). Chạy lại máy kiểm, thấy ✅ mới vẽ. Mac mới tinh: `python3` báo thiếu công cụ dành cho nhà phát triển → chạy `xcode-select --install`, người dùng bấm "Cài đặt", xong chạy lại máy kiểm.
   **Windows:** gõ `python scripts\kiem-cong-cu-ve.py` (lệnh in ra là PowerShell; bước nào cần hộp xin quyền, máy ghi "Bạn làm: bấm Yes"). Windows luôn có Edge nên không cần cài Chrome.

**Thứ tự: dùng thứ bạn ĐANG TRẢ trước, rồi mới tới API, cuối cùng mới tới công cụ chuyên nghiệp.**

| Tầng · đường | Tiền | Cần | Ảnh ra (đo thật 14–15/11/2026) |
|---|---|---|---|
| **1 · Gói ChatGPT — Codex tự vẽ** | 0đ thêm, trừ hạn mức gói | Gói Plus/Pro + Codex CLI đăng nhập bằng tài khoản ChatGPT | Đẹp nhất đã đo: người, tay, chữ nhãn gần đúng; ~1–2,5 phút/ảnh |
| **1 · Gói Gemini — Antigravity tự vẽ** | 0đ thêm, trừ hạn mức vẽ ảnh của gói (trần TUẦN riêng, hay cạn) | Gói Google AI Pro/Ultra + Antigravity CLI (`agy`) đã đăng nhập | ~1K, chữ Việt đúng dấu, nhận ảnh tham chiếu; **độ giữ sản phẩm CHƯA đo** (hết lượt tuần 15/11) |
| **1 · Claude tự dựng bằng code** | 0đ | Chỉ cần máy nền | Sản phẩm + nhãn đúng 100% (ảnh thật), kiểu ảnh đồ hoạ nền màu, KHÔNG có cảnh chụp; ~2 giây/ảnh |
| **2 · Seedream 4.5 (BytePlus, ByteDance)** | 200 ảnh miễn phí, sau đó ~0,04 USD/ảnh | Tài khoản BytePlus + thẻ/PayPal để kích hoạt (bật "chỉ dùng phần miễn phí") | Thứ 2 sau ChatGPT; chữ nhỏ hay sai ("336 g" → "136 g") ⇒ bắt buộc qua máy đọc chữ |
| **2 · Cloudflare** | 0đ, ~40 ảnh/ngày | Tài khoản Cloudflare miễn phí + Node | Kém nhất: ~1K, người/tay hay hỏng, hay bị chặn với sản phẩm màu đen / bao bì in người ⇒ dùng kiểu "cảnh trống + ghép sản phẩm thật" |
| **2 · Trả tiền: Gemini API / Seedream 5.5** | ~0,05 USD/ảnh 2K · ~0,036 USD/ảnh | Khoá có gắn thẻ | Ổn định, 2K — CHỈ khi người dùng tự chọn trả tiền |
| **3 · Công cụ chuyên nghiệp bạn đã dùng** (Photoroom, Pebblely, Canva…) | theo gói của bạn | Tài khoản / khoá API của bạn | Hợp lô lớn. Photoroom tự nhận chỉ ~38% ảnh sửa giữ đúng sản phẩm ⇒ vẫn qua đủ soát |

Gợi ý: có gói ChatGPT → đường đó. Có gói Gemini → Antigravity (hết lượt tuần thì sang đường kế). Chỉ có Claude → Claude tự dựng bằng code; muốn ảnh có cảnh chụp → Seedream 4.5 (200 ảnh miễn phí) hoặc Cloudflare. Mọi đường vẫn chạy đủ soát + máy đọc chữ + dán nhãn thật + đặt chữ. Phần Agent chạy tốn hạn mức gói Agent của bạn (~120 nghìn token/sản phẩm).
Đã xét, KHÔNG dùng (11/2026): web tự bấm (người dùng phải làm tay), vẽ trên máy (FLUX ăn ~17 GB RAM, máy 24 GB đơ cả giờ), Hugging Face, Pollinations (phải đưa ảnh hãng lên mạng công khai), các máy Trung Quốc qua fal (Qwen, Wan, Hunyuan, MiniMax: không hơn Seedream).

Dữ liệu gửi ra ngoài: ảnh hãng + lời nhờ đi sang OpenAI (gói ChatGPT), Google (gói Gemini, Gemini API), ByteDance/BytePlus (Seedream), Cloudflare, hoặc công cụ tầng 3; **Claude tự dựng bằng code không gửi ảnh đi đâu**. Nói rõ; KHÔNG dùng ảnh mật, sản phẩm chưa công bố. Khoá/token: KHÔNG bảo người dùng dán vào chat, KHÔNG in ra.

**Cài + nối:** máy kiểm in sẵn lệnh cho từng đường (môi trường Python riêng `~/.venv-anh-qc` khoá phiên bản, Chrome hoặc Edge để đặt chữ, Codex, Antigravity, công cụ dòng lệnh Apple, wrangler, thư viện Gemini). Chạy máy bằng `~/.venv-anh-qc/bin/python scripts/<máy>.py …`. **Lệnh `python` trong mọi hướng dẫn dưới đây = Python riêng mà `kiem-cong-cu-ve.py` in ra** (Mac `~/.venv-anh-qc/bin/python`; Windows `%USERPROFILE%\.venv-anh-qc\Scripts\python.exe`).
- **Gói ChatGPT:** máy vẽ tự từ chối khi Codex đăng nhập bằng khoá API (OpenAI sẽ tính tiền từng ảnh) — đăng nhập lại bằng tài khoản ChatGPT.
- **Gói Gemini:** chưa có `agy` → máy kiểm mở trang tải Antigravity; người dùng cài, đăng nhập tài khoản Google có gói, bật công cụ dòng lệnh theo hướng dẫn trong ứng dụng (chưa thử trên máy mới tinh).
- **Seedream (BytePlus):** người dùng đăng ký console.byteplus.com, BẬT "Free Credits Only Mode" trước, thêm thẻ/PayPal, Activate dòng Seedream 4.5, tạo khoá ở trang API Key → Agent chạy `kiem-cong-cu-ve.py --nhap-khoa byteplus` (ô kín). Thẻ/PayPal là việc của người dùng, Agent không nhập.
- **Cloudflare, bật cổng vẽ** (chạy nền suốt phiên): `npx wrangler dev --cwd scripts/cong-cloudflare-ai --port 8841 --ip 127.0.0.1` → thấy "Ready" là xong. Lần đầu → `npx wrangler login`. Nhiều account → thêm `account_id` vào `scripts/cong-cloudflare-ai/wrangler.toml`. Không dùng được wrangler → token mẫu "Workers AI", người dùng tự đặt `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`, bỏ `--cong`.
- **Gemini API trả tiền:** `kiem-cong-cu-ve.py --nhap-khoa gemini` (ô kín), máy vẽ đọc `~/.config/anh-qc/gemini.key`.

## Thư mục làm việc
```
<du-an>/anh-hang/        ảnh chính hãng (tho/ = ảnh tải về, bang-xem.jpg = bảng chọn có số)
<du-an>/the-san-pham.md  sự thật đếm trên ảnh hãng + danh sách CHỮ QUAN TRỌNG
<du-an>/loi-nho/ · ve/ (ảnh vẽ + so-chi.jsonl sổ tiền/lượt) · soat/ · sua/ · phang/ (mặt in ép phẳng, sản phẩm đã tách nền)
<du-an>/dat-chu/         cau-hinh.json + logo thật → ra/*.png + *.jpg
```

## Bước 1 — Gom ảnh chính hãng (không bỏ bước này)
`python scripts/gom-anh-hang.py "<link trang sản phẩm>" anh-hang` → tải ảnh ≥ 500px vào `anh-hang/tho/`, tự bỏ ảnh trùng khác cỡ, ghép `bang-xem.jpg` đánh số (trang chỉ có ảnh nhỏ → chạy lại thêm tham số `300` sau thư mục). Máy chỉ tải cùng tên miền với trang; nó báo tên miền bị bỏ — tên nào là kho ảnh của chính hãng/gian hàng (vd `product.hstatic.net` của gian Haravan) thì chạy lại kèm `--them-ten-mien <tên>`. **Trang chặn máy tải** (máy báo rõ) → KHÔNG lách: bảo người dùng mở trang bằng trình duyệt, chuột phải → Lưu ảnh vào `anh-hang/tho/`, rồi chạy `gom-anh-hang.py "<link>" anh-hang --chi-bang-xem`.
Cần đủ: toàn thân 3–4 góc, cận từng bộ phận dễ sai, đủ các màu bán, **ảnh mặt có chữ/nhãn cỡ ≥ 1000px** (để máy đọc chữ và dán nhãn thật cho nét), **1 ảnh nền trắng/trơn** (để tách nền cho đường "Claude tự dựng" và kiểu ghép). **Ảnh hãng phải NÉT:** mở `cat-phong-to.py` xem chữ nhỏ trên nhãn ở cỡ thật; nhoè, vỡ khối, hoặc sản phẩm chiếm < 800px → ảnh ra sẽ mờ theo (hộp cà phê 16/11: ảnh hãng 1000px, hộp 807px, ra ảnh nhoè). Xin người dùng ảnh tốt hơn: tự chụp sản phẩm thật bằng điện thoại (nền trơn, đủ sáng, chụp thẳng), hoặc gửi file thiết kế bao bì. Logo PNG/SVG trên trang hãng; logo < 400px chỉ đặt cỡ nhỏ (rộng ≤ 110px). Thiếu ảnh → xin người dùng chụp bằng điện thoại. Không có ảnh hãng thì KHÔNG vẽ. Hỏi 1 câu nếu chưa rõ: họ có được dùng ảnh/logo của hãng cho quảng cáo không.

## Bước 2 — Thẻ sản phẩm: ĐẾM trên ảnh, không đoán
Mở từng ảnh cận (`scripts/cat-phong-to.py`), ghi vào `the-san-pham.md` từng bộ phận: **số lượng**, **hình dạng**, **màu**, **chữ/logo in trên đó** (chép đúng từng chữ), **đối xứng** hay không, **bộ phận lệch bên nằm BÊN NÀO** (quai, tay cầm, nút, núm — "tay cầm ở 1/3 TRÁI mặt ngăn kéo"), **tỉ lệ cao : rộng bằng số** (hộp 1,9:1, chai 2,6:1), **rỗng hay đầy**, trong suốt hay không. Từ thẻ lập danh sách soát theo `references/danh-sach-soat-mau.md`.
**Danh sách CHỮ QUAN TRỌNG** (lập 1 lần, mọi lần soát dùng lại): 3–8 cụm khách cần đọc đúng — tên sản phẩm, khối lượng/dung tích, số/kiểu (vd "3in1"), khẩu hiệu chính. Chép đúng từng chữ, đúng dấu, đúng số. Bỏ chữ li ti mà cả ảnh hãng cũng không đọc nổi.

## Bước 3 — Lời nhờ vẽ từng cảnh
Theo khuôn `references/loi-nho-mau.md` (bối cảnh, góc máy, ánh sáng, chừa chỗ chữ bằng con số, tả sản phẩm chép từ thẻ, tỉ lệ bằng số, "KHÔNG chữ/logo/watermark"). Đính 1–3 ảnh hãng cùng góc nhất + **ảnh cận nhãn**. Kiểm kỹ ảnh mẫu trước khi đính: máy gom có thể lấy nhầm ảnh quảng cáo/biểu tượng của trang.
**Chống vẽ sai chữ khi để AI vẽ cả sản phẩm:** cho sản phẩm chiếm TO trong khung (mặt nhãn rộng ≥ 1/3 chiều rộng ảnh — hộp cà phê của Seedream sai số chính vì hộp quá nhỏ); không nhờ vẽ 2 sản phẩm cùng lúc. Sản phẩm đứng yên trên bàn/kệ mà ảnh hãng có góc hợp → dùng kiểu **cảnh trống + ghép sản phẩm thật** (Bước 4) thay vì để AI vẽ sản phẩm.
Mẹo riêng từng đường: cuối `references/loi-nho-mau.md`.

## Bước 4 — Vẽ (LẦN LƯỢT, không chạy song song — sổ không khoá)
- **Gói ChatGPT:** `python scripts/ve-anh-goi-chatgpt.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.png anh-hang/nhan.png --ti-le 4:5 --ra ve/canh-1-a.png` (~1–2,5 phút/ảnh). Codex báo model mặc định "not supported when using Codex with a ChatGPT account" → thêm `--model <1 tên trong ~/.codex/models_cache.json>` (15/11/2026 dùng được `gpt-5.6-sol`).
- **Gói Gemini:** `python scripts/ve-anh-goi-google.py --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.png anh-hang/nhan.png --ti-le 4:5 --ra ve/canh-1-a.png` (1–4 phút/ảnh; agy hay vẽ 2–3 bản, máy lấy bản cuối).
- **Claude tự dựng bằng code** (không AI vẽ):
  1. Tách nền ảnh hãng nền trơn: Mac → `swift scripts/tach-nen-san-pham.swift anh-hang/a.png phang/vat.png 0.5 0.5` (2 số = 1 điểm trên sản phẩm, tỉ lệ ảnh; ~6 giây). Windows, hoặc Vision lấy nhầm vật → `python scripts/tach-nen-don-gian.py anh-hang/a.png phang/vat.png` (còn dính bóng đổ dưới đáy → thêm `--nguong 40`). Mở xem trên nền tối: mép sạch, không mất góc hộp; lỗ xuyên (quai cốc, quai túi) không bị lấp mảng trắng (máy đơn giản lấp → dùng đường khác).
  2. Nền bằng code, màu lấy từ logo/bao bì hãng: `python scripts/ve-nen-bang-code.py --mau-chinh "#d4202a" --kieu toi --vong --co 1080x1350 1920x1080 1080x1920 --ra ve/` (`--kieu sang` cho mỹ phẩm, đồ trắng).
  3. Đặt sản phẩm: `python scripts/ghep-san-pham-that.py ve/nen-1080x1350.png phang/vat.png ve/canh-1-a.png --cao 0.42 --tam-x 0.5 --day-y 0.82` (sản phẩm TO, giữa-dưới, chừa trên ~35% cho chữ). Máy in CẢNH BÁO khi sản phẩm phải hiện > 80% cỡ ảnh gốc → hạ `--cao` theo số máy gợi ý, hoặc quay lại Bước 1 xin ảnh to hơn; KHÔNG giao ảnh có cảnh báo này.
  4. Bước 7 đặt chữ như mọi đường. Kết quả kiểu ảnh đồ hoạ (như ảnh Canva), không phải ảnh chụp — nói rõ với người dùng.
- **Cảnh trống + ghép sản phẩm thật** (dùng được với mọi đường vẽ): vẽ cảnh KHÔNG có sản phẩm (không đính ảnh hãng) → tách nền (như trên) → `python scripts/ghep-san-pham-that.py ve/canh-trong.png phang/vat.png ve/canh-1-a.png --cao 0.5 --tam-x 0.5 --day-y 0.74 --bong phai` (đáy sản phẩm đúng mặt bàn; bóng ngược phía nguồn sáng). Mở xem: chân sản phẩm phải "ngồi" trên mặt bàn, cỡ hợp đồ vật quanh. Sản phẩm đúng 100% nhưng chỉ ở đúng góc chụp của ảnh hãng.
- **Seedream (BytePlus):** `python scripts/ve-anh-byteplus.py --loi-nho … --mau … --ti-le 4:5 --ra ve/canh-1-a.png` (mặc định Seedream 4.5; `--model seedream-5-5-…` khi người dùng chọn trả tiền; `--tran-usd` mặc định 1).
- **Cloudflare:** `python scripts/ve-anh-mien-phi.py --cong http://127.0.0.1:8841 --loi-nho loi-nho/canh-1.txt --mau anh-hang/a.jpg --ti-le 4:5 --ra ve/canh-1-a.png` (~10 giây/ảnh; chạm 10.000 neuron/ngày thì dừng tới 7h sáng hôm sau).
- **Gemini API trả tiền:** `python scripts/ve-anh-nhieu-mau.py --loi-nho … --mau … --ti-le 4:5 --co 2K --ra ve/canh-1-a.png --tran-usd 2`. Mỗi ~1 USD báo người dùng 1 dòng.
- **Công cụ chuyên nghiệp (tầng 3):** người dùng nói tên công cụ + đưa khoá/tài khoản (ô kín, không qua chat); Agent đọc tài liệu API chính thức của công cụ đó, ưu tiên chức năng "tách nền + dựng nền" (giữ ảnh thật) hơn "sửa ảnh bằng AI"; ảnh ra vẫn qua Bước 5–7b.
Mọi đường để AI vẽ cả sản phẩm: vẽ 2 bản, giữ bản qua máy đọc chữ. Hết lượt / báo lỗi hạn mức → dừng, báo người dùng, KHÔNG tự sang đường trả tiền. Lỗi dáng lặp lại sau 2 lần FIX (vd quai đảo bên khi ngăn kéo mở) → đổi cảnh dễ hơn (ngăn kéo đóng, góc thẳng) thay vì vẽ tiếp.

## Bước 5 — Soát (CỔNG BẮT BUỘC, 3 lớp)
**5a. Máy đọc chữ** (Mac: Apple Vision · Windows: máy đọc chữ có sẵn của Windows; 0đ, ảnh không gửi đi đâu): `python scripts/doc-chu-so-sanh.py --hang anh-hang/nhan.png --ve ve/canh-1-a.png --chu "<từng chữ quan trọng ở Bước 2>" [--vung-ve x0,y0,x1,y1] [--vung-hang x0,y0,x1,y1]` (vùng = khung quanh nhãn, tỉ lệ 0–1; khung chặt đọc tốt hơn, chữ nhỏ như khối lượng "336 g" thường chỉ đọc ra khi cắt cả 2 ảnh). **TRƯỢT** (ảnh hãng đọc được, ảnh vẽ không thấy / sai số / sai dấu) → Bước 6 dán nhãn thật hoặc vẽ lại. **MÁY KHÔNG ĐỌC ĐƯỢC** → Agent tự phóng to soát mắt; chữ quan trọng mà ở cỡ ảnh giao vẫn không đọc nổi = CHƯA ĐẠT (không coi là qua). "Chữ lạ" máy liệt kê → xem có phải AI bịa chữ không. Windows chưa có gói tiếng Việt: máy so KHÔNG DẤU và báo rõ — dấu soát mắt kỹ ở 5b (thêm gói: Cài đặt → Ngôn ngữ → thêm Tiếng Việt). Linux: bỏ 5a, soát mắt kỹ hơn ở 5b.
**5b. Tự soát:** mỗi ảnh, cắt phóng to TỪNG vùng, ghép cạnh ảnh hãng cùng góc (`scripts/so-sanh-truoc-sau.py`), MỞ XEM, đi hết danh sách soát — kể cả 3 mục hay bị bỏ qua: **bộ phận lệch bên đúng BÊN**, **tỉ lệ cao:rộng khớp ảnh hãng** (đo bằng điểm ảnh, so với ảnh hãng CÙNG góc chụp — nhìn chéo 3/4 thì mặt hộp ngắn lại là đúng; lệch > 10% là trượt), **ám màu** (ánh sáng cảnh làm sản phẩm đổi màu so ảnh hãng), **độ nét** (cắt sản phẩm ở cỡ thật của ảnh giao: logo, chữ to trên nhãn phải sắc cạnh, không nhoè). Trượt 1 mục = loại hoặc sửa. Đường vẽ nào cũng phải soát, kể cả ảnh Claude tự dựng.
**5c. Trợ lý con soát độc lập:** giao ảnh + ảnh hãng + danh sách soát + thẻ, KHÔNG nói kết quả tự soát, đòi bảng ĐẠT/TRƯỢT từng mục có lý do. Ca mẫu: tự soát cho qua 9 ảnh, trợ lý độc lập loại 6.
Đường "Claude tự dựng" và kiểu ghép sản phẩm thật: sản phẩm là ảnh thật nên bỏ 5a; vẫn soát mép tách nền, cỡ, bóng.

## Bước 6 — Sửa (dán chi tiết thật, không vẽ lại cả ảnh)
**Sản phẩm có chữ nhỏ / nhãn / mặt in (chai, hộp, túi, bìa sách) mà máy đọc chữ báo TRƯỢT hoặc soát mắt thấy sai → dán mặt in thật.**
**Ngoại lệ:** máy đọc chữ ĐẠT + phóng to so ảnh hãng đúng từng chữ → KHÔNG dán (thử 4 sản phẩm gói ChatGPT 15/11/2026: nhãn AI vẽ đã đúng, dán ảnh hãng nhỏ/mờ còn xấu hơn). Chỉ dán khi chữ sai VÀ ảnh mặt in của hãng ≥ 1000px.
1. Ép phẳng mặt in 1 lần: `python scripts/ep-phang.py anh-hang/a.png "TL TR BR BL" <rộng> <cao> phang/mat-truoc.png` (4 góc mặt in trên ảnh hãng, đo bằng `cat-phong-to.py`).
2. Dán vào từng cảnh: `python scripts/dan-chi-tiet-that.py phang/mat-truoc.png "0,0 W,0 W,H 0,H" ve/canh-1-a.png "<4 góc đích>" sua/canh-1.png [khop] [no] [hinh] [mo] [--giu "<đa giác vật che>"] [--vung "<đa giác viền túi>"] [--co-vao 3]`
   - `--giu`: vật đứng TRƯỚC mặt in (tách cà phê, ngón tay) — giữ nguyên ảnh AI ở đó.
   - `--vung`: mặt in không phẳng chữ nhật (túi, bao) — chỉ dán trong viền này, khỏi lộ khung.
   - `--co-vao`: co mép nguồn vài điểm ảnh, khỏi dính viền nền trắng ảnh hãng.
   - `--khop-vung 80`: mặt in có dải sáng/màu chuyển dần (túi vàng→xanh, nắng rọi 1 bên) → khớp sáng theo từng vùng, hết lộ khung.
| Lỗi khác | Cách sửa |
|---|---|
| Logo méo (1 màu) | `scripts/thay-logo.py`; logo nhiều màu → `dan-chi-tiet-that.py` |
| Chi tiết dài 2 đầu tròn | `khung-vien-thuoc.py` ra 4 góc, dán với `hinh=vien` |
| Hai bên lệch (vật đối xứng) | Lật gương nửa đúng sang nửa sai (Pillow `ImageOps.mirror`, mép mềm) |
| Màu sai / ám màu | Đổi màu theo vùng (HSV) chỉ trên phần sản phẩm, so ảnh màu hãng |
| Chữ trên mặt cong / nghiêng (hông giày) | Nắn theo hình chữ nhật xoay theo hướng chữ, chừa lề cuối chữ, `--vung` theo viền mảng; vẫn lộ khung → bỏ, thiếu chữ nhỏ còn hơn chữ lộ khung |
| Vệt mờ nhỏ trên hoa văn lặp | Nhỏ, không thấy ở cỡ đăng → chấp nhận, ghi báo cáo; thấy rõ → vẽ lại |
| Dáng / tay chân / bộ phận sai bên | Vẽ lại kèm FIX; 2 lần không được → đổi cảnh (Bước 4) |
| **Vật TRONG SUỐT** (bình sữa, chai thuỷ tinh) | Chưa dán được (thấy cảnh xuyên qua). Chỉ FIX bằng chữ, ghi từng số vạch; nói trước với người dùng chữ/vạch nhỏ có thể sai |
Dán xong: chạy lại máy đọc chữ + soát đúng vùng đó (phóng to, so ảnh hãng), mép dán không lộ.

## Bước 7 — Đặt chữ (AI không vẽ chữ)
Chép `references/mau-dat-chu.json` vào `dat-chu/cau-hinh.json`, điền ảnh nền, logo THẬT, các dòng chữ, **màu lấy từ logo hãng** (không để màu mẫu), web. Kiểu chữ `kieu_chu`: `nghieng-dam` (khoẻ, xe/thể thao) · `dam` (gia dụng, thực phẩm) · `thanh-lich` (mỹ phẩm, sách, thời trang). Nền tối → `"nen_toi": true`. Logo trên nền rối/tối → `"the": true`. Logo hãng chỉ là ô biểu tượng nền đặc (vd ô chữ "M" đen) → chỉ đặt trên nền cùng tông, nền khác thì bỏ logo. Mở ảnh nền xem đầu người / sản phẩm nằm đâu rồi mới đặt `khoi`. Chạy `python scripts/dat-chu.py dat-chu/cau-hinh.json` → ra cả PNG và JPG. Mở từng ảnh soát: chữ không chạm mặt/tay người, không đè chi tiết chính, dấu tiếng Việt đúng, không xuống dòng giữa cụm từ.
Câu chữ: chỉ từ sự thật trên trang hãng; không giá/khuyến mãi/"số 1"/công dụng chữa bệnh khi người dùng chưa đưa; người dùng duyệt trước khi đặt.

## Bước 7b — Đóng vai khách hàng xem lại (CỔNG BẮT BUỘC trước khi giao)
Soát ở Bước 5 hỏi "sản phẩm có đúng không"; bước này hỏi "**khách có dừng lại, hiểu, tin không**" — người làm ảnh nhìn lâu sẽ quen mắt, không thấy được.
1. Giao trợ lý con (không gọi được trợ lý con → Agent tự đóng vai, chỉ nhìn ảnh): ảnh ĐÃ đặt chữ, thu về cỡ màn điện thoại (rộng ~400px) + ảnh cỡ thật + chân dung khách (Bước 0). KHÔNG đưa lời nhờ vẽ, thẻ sản phẩm, ý đồ — khách thật không biết những thứ đó. Gom mọi ảnh của 1 sản phẩm vào 1 lượt (mỗi lượt trợ lý con ~100 nghìn token hạn mức gói Agent). Dặn: "Bạn là [chân dung], đang lướt [Facebook/TikTok]. Trả lời như người bình thường, chỉ nêu chỗ chắc chắn vấp."
2. Người xem trả lời 5 câu: (1) Lướt 2 giây, mắt dừng ở đâu đầu tiên, có dừng lại không? (2) Ảnh bán gì, cho ai — nói lại bằng lời mình. (3) Chữ đọc được ở cỡ điện thoại không, câu nào khó hiểu / nghe như quảng cáo dịch? (4) Chỗ nào trông giả, "ảnh AI", làm mất tin (sản phẩm méo, tay lạ, cảnh không giống Việt Nam, đồ vật vô lý)? (5) Có muốn bấm xem / hỏi giá không, vì sao?
3. Agent chính lọc: GIỮ lỗi ai nhìn cũng vấp (không hiểu bán gì, chữ không đọc được, chỗ giả rõ, sản phẩm chìm). BỎ ý thích riêng, đòi thêm thông tin, đòi đổi thông điệp người dùng đã duyệt (ghi lại để báo, không tự đổi). Sửa (cỡ/chỗ đặt chữ, cắt khung, vẽ lại cảnh, bỏ ảnh) → cho người xem nhìn lại. Tối đa 2 vòng.
Thử 15/11/2026 (nước tẩy trang, 2 ảnh đã qua soát sản phẩm): người xem bắt được vệt son trên bông trông như vết máu, tiêu đề chữ có chân màu nhạt khó đọc ở cỡ điện thoại, miếng bí đao trông như dưa gang — những lỗi không nằm trên sản phẩm nên Bước 5 không bắt.

## Bước 8 — Giao
`1-anh-xong/` (JPG 92) · `2-anh-nen-chua-chu/` · `3-so-sanh/` (nếu cần). Báo 1 tin: bao nhiêu ảnh, đường vẽ + tiền/lượt đã dùng (đọc `ve/so-chi.jsonl`), kết quả máy đọc chữ, ảnh nào bỏ và vì sao, **người xem thử thấy gì + đã sửa gì** (2–3 dòng), chỗ còn non (nói thật).

## Không làm
- Không bắt người dùng tự gõ lệnh hay tự cài thứ Agent cài được. Không vẽ khi chưa có ảnh hãng. Không giao ảnh chưa qua soát (Bước 5) + khách xem thử (Bước 7b). Không tự chuyển sang đường trả tiền (kể cả khi gói / phần miễn phí hết lượt — báo người dùng, chờ hồi lượt hoặc để họ chọn).
- Không dùng dịch vụ "miễn phí" đòi đưa ảnh hãng lên mạng công khai, hay đòi dán khoá/mật khẩu vào chat. Không nhập thẻ/PayPal thay người dùng.
- Không để AI vẽ chữ quảng cáo, logo, giá, số điện thoại. Không vẽ người nổi tiếng / người thật nhận ra được. Không vẽ logo hãng khác. Không vẽ sản phẩm chỉ từ mô tả chữ (không đính ảnh hãng) — nhãn bịa ra thì không sửa nổi.
- Không tự nâng trần tiền. Không lách trang hãng chặn tải.

## Tham khảo
- `references/vi-du-xe-may-dien.md` — ca mẫu đầy đủ (xe điện). `references/danh-sach-soat-mau.md` · `references/loi-nho-mau.md` · `references/mau-dat-chu.json`
