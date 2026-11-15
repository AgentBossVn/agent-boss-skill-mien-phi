// Tách sản phẩm khỏi nền ảnh hãng bằng Vision của macOS (chạy trên máy, 0đ, không gửi ảnh đi đâu).
// Chạy: swift tach-nen-san-pham.swift anh-hang.png ra.png [x y]   — x y (0–1, gốc trên-trái) = 1 điểm nằm trên sản phẩm
//       để chọn đúng vật khi ảnh có nhiều vật (vd huy chương, tay). Không có ⇒ lấy mọi vật nổi.
import Foundation
import Vision
import CoreImage
import AppKit

let a = CommandLine.arguments
guard a.count >= 3 else { print("Cách chạy: swift tach-nen-san-pham.swift vao.png ra.png [x y]"); exit(1) }
let url = URL(fileURLWithPath: a[1])
// .applyOrientationProperty: ảnh chụp điện thoại (thẻ EXIF xoay) ra đúng chiều
guard let ci = CIImage(contentsOf: url, options: [.applyOrientationProperty: true]) else { print("Không đọc được ảnh"); exit(1) }
let req = VNGenerateForegroundInstanceMaskRequest()
let h = VNImageRequestHandler(ciImage: ci)
do { try h.perform([req]) } catch { print("Vision lỗi: \(error)"); exit(1) }
guard let kq = req.results?.first else { print("Không thấy vật nổi nào"); exit(1) }
var chon = kq.allInstances
if a.count >= 5, let x = Double(a[3]), let y = Double(a[4]) {
    let m = kq.instanceMask  // CVPixelBuffer, mỗi điểm = số thứ tự vật (0 = nền)
    CVPixelBufferLockBaseAddress(m, .readOnly)
    let w = CVPixelBufferGetWidth(m), hh = CVPixelBufferGetHeight(m), bpr = CVPixelBufferGetBytesPerRow(m)
    let p = CVPixelBufferGetBaseAddress(m)!.assumingMemoryBound(to: UInt8.self)
    let v = Int(p[max(0, min(hh - 1, Int(y * Double(hh)))) * bpr + max(0, min(w - 1, Int(x * Double(w))))])
    CVPixelBufferUnlockBaseAddress(m, .readOnly)
    if v == 0 { print("Điểm (\(x),\(y)) rơi vào nền — chọn điểm khác"); exit(1) }
    chon = IndexSet(integer: v)
}
do {
    let buf = try kq.generateMaskedImage(ofInstances: chon, from: h, croppedToInstancesExtent: true)
    let out = CIImage(cvPixelBuffer: buf)
    let ctx = CIContext()
    try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: a[2]), format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
    print("OK \(a[2]) \(Int(out.extent.width))x\(Int(out.extent.height)) · \(kq.allInstances.count) vật, lấy \(chon.count)")
} catch { print("Lỗi xuất: \(error)"); exit(1) }
