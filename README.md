# Kho skill miễn phí của Agent Boss

Đây là nơi Agent Boss chia sẻ các skill miễn phí cho bạn mang về dùng. Hiểu đơn giản thì skill là bộ hướng dẫn kèm công cụ để Agent trên máy bạn (như Claude Code, Codex hay Antigravity) tự làm trọn một việc từ đầu đến cuối.

Hiện tại kho có 1 skill là **Ảnh quảng cáo sản phẩm** nằm trong thư mục `anh-quang-cao-san-pham`. Các skill khác mình sẽ thêm dần vào đây.

## Skill "Ảnh quảng cáo sản phẩm" làm gì?

Khi bạn nhờ AI vẽ ảnh quảng cáo, lỗi hay gặp nhất là sản phẩm bị vẽ sai chữ trên nhãn, sai số khối lượng, hoặc thừa thiếu chi tiết. Skill này giúp Agent làm ra ảnh quảng cáo có sản phẩm thật của bạn, giữ đúng dáng, đúng logo, đúng từng chữ trên nhãn như ảnh của hãng.

Khi nhận việc, Agent sẽ tự làm các bước:
- Tải ảnh sản phẩm từ trang của hãng, đếm từng chi tiết trước khi vẽ.
- Vẽ ảnh bằng công cụ do bạn chọn.
- Dùng máy đọc chữ để so chữ trên nhãn ảnh vừa vẽ với ảnh gốc của hãng (bắt được cả những lỗi kiểu "336 g" bị vẽ thành "136 g").
- Chỗ nào vẽ sai thì lấy nhãn thật của hãng dán đè lên.
- Đặt chữ quảng cáo lên ảnh.
- Tự đóng vai khách hàng của bạn để xem lại ảnh rồi sửa tiếp, xong xuôi mới đưa bạn duyệt.

## Vẽ bằng gì và tốn bao nhiêu?

Agent sẽ tự kiểm tra máy của bạn rồi in ra một bảng cho bạn chọn. Công cụ nào chưa có trên máy thì Agent tự cài, chỉ nhờ bạn làm những bước bắt buộc người làm như đăng nhập.

- **Ưu tiên gói AI bạn đang trả tiền, không tốn thêm chi phí:** dùng gói ChatGPT Plus/Pro (qua Codex, cho ảnh đẹp nhất mà mình đã đo), gói Google AI Pro (qua Antigravity), hoặc để Agent tự dựng ảnh bằng code từ ảnh thật của sản phẩm (tốn 0đ, sản phẩm đúng 100%, ra kiểu ảnh đồ hoạ chứ không phải ảnh chụp).
- **Nếu bạn chưa có gói nào:** dùng Seedream 4.5 của BytePlus được 200 ảnh miễn phí (cần thêm thẻ Visa/Master hoặc PayPal để kích hoạt), hoặc dùng Cloudflare miễn phí khoảng 40 ảnh/ngày (cho chất lượng ảnh kém nhất).
- **Trả tiền theo lượt chỉ khi bạn tự chọn:** dùng Gemini API tốn khoảng 0,05 USD/ảnh. Agent không bao giờ tự ý chuyển sang đường tốn tiền.
- **Phần việc của Agent (đọc, soát lỗi, đặt chữ):** tính vào hạn mức gói Agent bạn đang dùng, hết khoảng 120 nghìn token cho 1 sản phẩm.

## Bạn cần chuẩn bị gì?

Bạn chỉ cần có Claude Code (hoặc Codex, Antigravity) chạy trên máy Mac hoặc Windows 10/11. Phần Python và các thư viện cần thiết thì Agent sẽ tự cài vào một thư mục riêng, không đụng chạm đến các phần mềm khác trên máy của bạn.

## Cách cài đặt và cập nhật

Bạn mở Agent lên, nhắn nguyên câu này để Agent tự tải về đúng chỗ:

```text
Cài skill anh-quang-cao-san-pham từ https://github.com/AgentBossVn/agent-boss-skill-mien-phi
```

Khi muốn cập nhật bản mới, bạn nhắn:

```text
Cập nhật skill anh-quang-cao-san-pham từ https://github.com/AgentBossVn/agent-boss-skill-mien-phi
```

## Cách dùng

Bạn nhắn cho Agent theo mẫu:

```text
Làm ảnh quảng cáo cho sản phẩm X, link trang sản phẩm: ...
```

Agent sẽ hỏi bạn vài câu (ảnh dùng để đăng đâu, cỡ nào, chọn công cụ vẽ nào) rồi bắt đầu làm.

Nếu là sản phẩm của chính bạn và trên mạng chưa có ảnh, Agent sẽ nhờ bạn lấy điện thoại chụp sản phẩm (chụp thẳng, nền trơn, đủ sáng) hoặc gửi file thiết kế bao bì. Ảnh gốc của hãng mà mờ thì ảnh làm ra cũng sẽ mờ theo.

## Một vài điều cần nhớ

Ảnh sản phẩm sẽ được gửi sang dịch vụ vẽ mà bạn chọn, vì vậy bạn đừng đưa những sản phẩm chưa công bố vào làm. Nếu có dùng khoá API, bạn nhập vào ô kín do Agent mở ra, tuyệt đối không dán thẳng vào khung chat.

## Điều khoản sử dụng

Bạn được dùng miễn phí cho công việc của bạn và doanh nghiệp của bạn. Không bán lại skill, không đóng gói lại thành khoá học hay sản phẩm khác.

Tác giả: Agent Boss (Mai Xuân Đạt).

## Học thêm

Nếu bạn muốn học cách tự xây Agent cho công việc của mình, mời bạn xem khoá học của Agent Boss tại https://agentboss.vn.