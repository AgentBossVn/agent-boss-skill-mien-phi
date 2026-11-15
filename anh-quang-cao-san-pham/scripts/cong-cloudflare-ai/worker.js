// Nhận form multipart (prompt, input_image_0..3, width, height, steps) → gọi FLUX.2 trên Workers AI → trả ảnh.
// Chỉ chạy qua wrangler dev trên máy. Đường: POST /ve?model=@cf/black-forest-labs/flux-2-klein-4b
const CHO_PHEP = new Set(['@cf/black-forest-labs/flux-2-klein-4b']);
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (req.method !== 'POST' || u.pathname !== '/ve') return new Response('POST /ve', { status: 404 });
    // Trang web lạ đang mở trong trình duyệt không gửi được header riêng (trình duyệt hỏi trước, cổng không trả lời) ⇒ không ăn trộm neuron được
    if (req.headers.get('x-anh-qc') !== '1') return new Response('thiếu dấu X-Anh-QC', { status: 403 });
    const model = u.searchParams.get('model') || '@cf/black-forest-labs/flux-2-klein-4b';
    if (!CHO_PHEP.has(model)) return new Response('model không cho phép', { status: 400 });
    try {
      const out = await env.AI.run(model, { multipart: { body: req.body, contentType: req.headers.get('content-type') } });
      const b64 = out && out.image;
      if (!b64) return new Response('không có ảnh: ' + JSON.stringify(out).slice(0, 300), { status: 502 });
      const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
      return new Response(bytes, { headers: { 'content-type': 'application/octet-stream' } });
    } catch (e) {
      return new Response('LỖI ' + String((e && e.message) || e).slice(0, 400), { status: 502 });
    }
  },
};
