// Local video occlusion masks. Compile with xcrun swiftc -O.
// Input is an ordered decoded frame sequence; never a set of unrelated takes.
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

guard CommandLine.arguments.count == 3 else {
    fputs("Usage: person-matte INPUT_FRAME_FOLDER OUTPUT_MASK_FOLDER\n", stderr)
    exit(2)
}
let input = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let frames = try FileManager.default.contentsOfDirectory(at: input, includingPropertiesForKeys: nil)
    .filter { ["png", "jpg"].contains($0.pathExtension.lowercased()) }.sorted { $0.lastPathComponent < $1.lastPathComponent }
guard !frames.isEmpty else { fatalError("No frames") }
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
let handler = VNSequenceRequestHandler()
let context = CIContext(options: [.cacheIntermediates: false])
for (index, frame) in frames.enumerated() {
    try autoreleasepool {
        guard let image = CIImage(contentsOf: frame) else { fatalError("Bad image: \(frame)") }
        try handler.perform([request], on: image, orientation: .up)
        guard let buffer = request.results?.first?.pixelBuffer else { fatalError("No person mask at \(index)") }
        let mask = CIImage(cvPixelBuffer: buffer)
        let resized = mask.transformed(by: CGAffineTransform(scaleX: image.extent.width / mask.extent.width,
                                                             y: image.extent.height / mask.extent.height))
        guard let cg = context.createCGImage(resized, from: image.extent, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray()),
              let dest = CGImageDestinationCreateWithURL(output.appendingPathComponent(frame.deletingPathExtension().lastPathComponent + ".png") as CFURL,
                                                         UTType.png.identifier as CFString, 1, nil) else { fatalError("Mask output failed") }
        CGImageDestinationAddImage(dest, cg, nil)
        guard CGImageDestinationFinalize(dest) else { fatalError("PNG output failed") }
    }
    if index % 30 == 0 { fputs("Mask \(index + 1)/\(frames.count)\n", stderr) }
}
print("Generated \(frames.count) masks")
