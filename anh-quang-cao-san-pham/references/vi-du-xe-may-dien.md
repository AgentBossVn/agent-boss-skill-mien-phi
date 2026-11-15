# Ca mẫu: ảnh quảng cáo xe máy điện (lớp Marketing — Agent Boss, 11/2026)

**Đầu bài:** người của hãng nhờ ChatGPT làm ảnh quảng cáo → ảnh đẹp, đúng xe, ưng (đó là chuẩn để so). Nhờ Agent của mình làm → ảnh xấu: xe studio ghép lên nền, lệch ánh sáng, thiếu bóng, sai tỷ lệ người–xe, một nền lặp cả bộ. Cần 5–10 ảnh đẹp ngang ảnh mẫu và ĐÚNG xe.

**Vì sao Agent của học viên làm hỏng:**
- Ghép rời ảnh nền + ảnh người + ảnh xe studio → không chung ánh sáng, không bóng, tỷ lệ lệch.
- Bộ nhận diện lấy nhầm xe mẫu khác làm chuẩn → ảnh tĩnh, nhạt.
- Lời giao việc chung chung, không nêu chi tiết xe; không soát từng vùng.

**Lần làm lại đầu tiên cũng chưa đạt:** Agent dùng máy vẽ ảnh khác, Agent báo đã soát nhưng chỉ nhìn lướt cả ảnh → người duyệt bắt 4 lỗi: đèn pha 3 thấu kính (xe thật 2), yếm lệch hai bên, chân người sai, chữ đè lên đầu người. AI vẽ đẹp ≠ AI vẽ đúng.

**Cách làm lại:**
1. Tải ~20 ảnh hãng: toàn xe nhiều góc, cận mặt nạ, đồng hồ, đuôi, bánh, cổng USB, cốp, 10 màu.
2. Đếm trên ảnh: đèn pha 2 thấu kính · ô mặt nạ 4 thanh mạ · logo nền đen biểu tượng cánh + ô vuông + chữ tên hãng · biển ghi tên hãng + khẩu hiệu + trang web hãng · xi nhan trước nửa tròn · màu hồng của hãng là trắng hồng rất nhạt.
3. Lời nhờ tả từng chi tiết bằng số, đính 2–4 ảnh hãng cùng góc; AI vẽ cảnh KHÔNG chữ.
4. 33 lượt vẽ Gemini 3 Pro Image (2K) ≈ 4,4 USD cho 9 ảnh cuối.
5. Tự soát cho qua 9 ảnh → trợ lý con soát độc lập loại 6.
6. Sửa 6 ảnh không vẽ lại: dán ô mặt nạ 4 thanh thật (3 ảnh), thay logo méo (4 ảnh), dán biển số thật (2 ảnh), lật gương nửa đèn pha để còn 2 thấu kính, xoá chữ lạ trên biển nền, đổi màu xe hồng đậm về đúng màu hãng.
7. Đặt chữ + logo thật bằng HTML (phông Be Vietnam Pro), chữ tránh mặt và tay người.

**7 lỗi soát ra và sửa (để dạy):** mặt nạ 9 sọc → 4 thanh + logo · đèn pha 3 thấu kính → 2 · logo mặt nạ méo (đọc ra thành tên một hãng xe khác) → logo thật · biển số méo → biển thật · biển ghi sai 1 chữ cái tên hãng → đúng tên · xe hồng đậm → đúng màu hãng · đồng hồ số 80 → 30.

**Bài học:**
- AI vẽ đẹp ≠ AI vẽ đúng. Đúng đến từ ảnh hãng + lời tả có số + soát phóng to.
- Người làm tự soát dễ "thấy điều mình muốn thấy" → luôn có 1 lớp soát độc lập.
- Sửa chỗ nhỏ bằng chi tiết thật nhanh và rẻ hơn vẽ lại cả ảnh.
- Thầy/người bán phải tự soi trước khi khách soi.
