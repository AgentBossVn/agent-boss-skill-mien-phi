# Khuôn lời nhờ vẽ 1 cảnh (viết tiếng Anh cho AI vẽ hiểu tốt nhất; tả sản phẩm phải chép từ thẻ sản phẩm)

```
Photorealistic advertising photo, <tỉ lệ> composition.
SCENE: <bối cảnh cụ thể: đường phố Hà Nội buổi sáng, cổng trường, quán cà phê…>, <thời điểm, thời tiết>.
PERSON: <tuổi, giới, trang phục, kiểu tóc>, <tư thế: ngồi trên xe, hai tay nắm tay lái, chân trái chống đất…>,
  natural face, exactly five fingers on each visible hand, anatomically correct legs.
CAMERA: <góc 3/4 phía trước / ngang / thấp>, <tiêu cự 35–85mm>, product sharp, background softly blurred.
LIGHT: <nắng sớm ấm / ánh sáng studio mềm>, consistent shadows under product and feet.
LAYOUT: the top <30>% of the frame is empty <wall / sky> with nothing in it; the person's head is below <35>% of the image height;
  keep the <góc trên trái / nửa phải> area clean for text overlay added later. (Ghi bằng số — câu chung chung AI hay bỏ qua.)
PRODUCT — must match the attached reference photos exactly:
- <bộ phận 1>: <hình dạng>, EXACTLY <n> <chi tiết>, <màu>
- <bộ phận 2>: ...
- <bộ phận đối xứng>: left and right sides perfectly symmetrical
- <bộ phận lệch bên>: the <handle> is on the LEFT third of the <drawer front> (as in the reference)
- proportions: height is <2.6>x the width; <empty / filled> <bottle>; <flat sealed bag, NO carry handle>
- color: <màu chính xác theo ảnh hãng>
DO NOT: add any text, letters, numbers, logos, watermarks or signs anywhere in the image;
  do not add extra lights, buttons or parts that are not in the reference photos.
```

Mẹo đã kiểm chứng:
- AI hay vẽ sai đúng những chỗ KHÔNG được tả → chi tiết nào dễ sai thì tả bằng số ("EXACTLY 2 round lenses").
- Đính ảnh hãng cùng góc với cảnh. Góc khác nhau thì AI phải tự xoay → dễ sai.
- Muốn bắt chước ảnh mẫu bạn ưng: tả lại bằng chữ (bố cục, ánh sáng, tông màu, khoảng trống cho chữ), đừng đính ảnh mẫu nếu trong đó sản phẩm sai.
- Vẽ lại sau khi soát trượt: thêm 1 dòng "FIX: <chỗ sai lần trước> → <đúng phải thế nào>".
- Tỉ lệ ghi bằng số ("height 1.9x width, flat box") — không ghi thì AI hay vẽ hộp vuông / chai kéo cao như ống.
- Vật có thể rỗng/đầy (bình, chai) → ghi rõ; đầy thì che mất vạch và nhãn. Túi/bao → "NO carry handle" nếu thật không có quai.
- Khung dọc/story hay bị chừa 1 dải phẳng trống ở mép → thêm "no empty bands, the scene fills the whole frame edge to edge".
- Đường Cloudflare (klein, miễn phí): máy chép sát bố cục ảnh mẫu → chỉ đính 1–2 ảnh sản phẩm sạch nền trơn, không tay người, thấy rõ mặt ngoài (ảnh nằm úp làm sai dáng); thêm "copy only the product, not the background"; tránh cảnh có người. Không ghi mã màu dạng #F1EBDD (Cloudflare từng chặn lời nhờ) — tả màu bằng chữ. Đồ nội thất dài → cảnh rộng, xa (cận cảnh hay mất gối/gãy chân). Hộp dẹt trong khung 9:16 klein hay vẽ thành hộp cao → dùng đường ghép hoặc cắt từ ảnh dọc. Báo lỗi 3030 "flagged" (hay gặp: bao bì in hình người, sản phẩm màu đen) → chạy lại 1 lần; vẫn bị thì đổi ảnh mẫu hoặc sang đường ghép; lượt bị chặn không tốn neuron.
- Đường GHÉP — cảnh phải CẬN và CÓ ĐẠO CỤ (bàn trống + tường trơn = ảnh xấu, đã bị chê 16/11/2026). Khuôn: "Close-up product photography backdrop, camera low and close to the <mặt bàn>, the surface fills the lower 35% of the frame. In the center-bottom there is an EMPTY spot about <45%> of the frame height (a product is placed there later). Around the empty spot, styled props that belong to using the product: <3–5 đạo cụ, vd sách: tách cà phê, kính, sổ tay mở, bút, chậu cây nhỏ>, some in the foreground slightly out of focus, some behind. Background softly blurred with depth (<cửa sổ, kệ, rèm>), warm directional light from the <left>, soft shadows falling to the <right>. Upper 30% calm and uncluttered for text. No products, no packaging, no text, no people." Đạo cụ phải thấp hơn sản phẩm, không che chỗ trống; ghi rõ sáng từ bên nào để đặt `--bong` ngược phía đó.
- Đường GHÉP (AI chỉ vẽ cảnh trống): lời nhờ tả cảnh + "the center of the <counter> is EMPTY (free space for a product placed later)" + "no bottles, no products, no packaging, no text"; ghi rõ mặt bàn nằm ở bao nhiêu % chiều cao và ánh sáng từ bên nào (để đặt bóng đổ đúng phía). Góc máy cảnh phải gần góc chụp ảnh hãng (thường ngang tầm mắt).
- Đường GÓI ChatGPT: vẽ được người, tay, chữ nhãn gần đúng; vẫn qua máy đọc chữ, sai thì dán nhãn thật (chữ rất nhỏ vẫn méo).
- Đường Seedream 4.5: dáng, màu đúng; chữ nhỏ hay sai số/dấu (hộp cà phê: "336 g" → "136 g", "THỨ THIỆT" → "thủ thiết") → cho nhãn chiếm to trong khung, đính ảnh cận nhãn, luôn qua máy đọc chữ.
- Đường GÓI Gemini (Antigravity): lời nhờ phải gọi tên tệp ảnh mẫu (`@mau-1.jpg`) và dặn dùng làm ảnh tham chiếu — máy vẽ đã tự thêm.
