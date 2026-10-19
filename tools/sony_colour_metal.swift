import Foundation
import AVFoundation
import CoreImage
import CoreVideo
import Metal

func fail(_ s: String) -> Never { fputs(s + "\n", stderr); exit(1) }
let args = CommandLine.arguments
if args.count != 4 { fail("usage: colour_gpu input LUT output.mov") }
let sourceURL = URL(fileURLWithPath: args[1]); let lutURL = URL(fileURLWithPath: args[2]); let outputURL = URL(fileURLWithPath: args[3])
if FileManager.default.fileExists(atPath: outputURL.path) { fail("Output exists") }
let lines = try String(contentsOf: lutURL, encoding: .utf8).components(separatedBy: .newlines)
var n = 0; var cube = [Float]()
for line in lines {
 let p = line.split(whereSeparator: { $0.isWhitespace })
 if p.first == "LUT_3D_SIZE", p.count == 2 { n = Int(p[1]) ?? 0 }
 if p.count == 3, let r = Float(p[0]), let g = Float(p[1]), let b = Float(p[2]) { cube += [r,g,b,1] }
}
if n < 2 || cube.count != n*n*n*4 { fail("Invalid LUT") }
let cubeData = cube.withUnsafeBufferPointer { Data(buffer: $0) }
guard let device = MTLCreateSystemDefaultDevice() else { fail("Metal unavailable") }
let context = CIContext(mtlDevice: device, options: [.workingColorSpace: NSNull(), .outputColorSpace: NSNull(), .cacheIntermediates: false])
let filter = CIFilter(name: "CIColorCube")!; filter.setValue(n, forKey: "inputCubeDimension"); filter.setValue(cubeData, forKey: "inputCubeData")
let asset = AVURLAsset(url: sourceURL)
guard let track = asset.tracks(withMediaType: .video).first else { fail("Missing video") }
let reader = try AVAssetReader(asset: asset)
let ro = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
ro.alwaysCopiesSampleData = false; reader.add(ro)
let width = Int(track.naturalSize.width); let height = Int(track.naturalSize.height)
let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mov)
let settings: [String: Any] = [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height,
 AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2, AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
 AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 45_000_000, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel, AVVideoExpectedSourceFrameRateKey: track.nominalFrameRate, AVVideoAllowFrameReorderingKey: false]]
let wi = AVAssetWriterInput(mediaType: .video, outputSettings: settings); wi.expectsMediaDataInRealTime = false; wi.transform = track.preferredTransform
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: wi, sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA, kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height, kCVPixelBufferMetalCompatibilityKey as String: true])
writer.add(wi)
if !writer.startWriting() { fail("Writer: \(String(describing: writer.error))") }; writer.startSession(atSourceTime: .zero)
if !reader.startReading() { fail("Reader: \(String(describing: reader.error))") }
let done = DispatchSemaphore(value: 0); let queue = DispatchQueue(label: "colour")
var count = 0
let start = Date()
wi.requestMediaDataWhenReady(on: queue) {
 while wi.isReadyForMoreMediaData {
  autoreleasepool {
   guard let sample = ro.copyNextSampleBuffer() else {
    wi.markAsFinished()
    if reader.status == .failed { fail("Decode: \(String(describing: reader.error))") }
    writer.finishWriting { done.signal() }
    return
   }
   guard let input = CMSampleBufferGetImageBuffer(sample), let pool = adaptor.pixelBufferPool else { fail("Missing pixel buffer") }
   var output: CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil, pool, &output)
   guard let output = output else { fail("Allocation failed") }
   let image = CIImage(cvPixelBuffer: input, options: [.colorSpace: NSNull()]);filter.setValue(image, forKey: kCIInputImageKey)
   guard let graded = filter.outputImage else { fail("LUT failed") }
   context.render(graded, to: output, bounds: CGRect(x: 0, y: 0, width: width, height: height), colorSpace: nil)
   if !adaptor.append(output, withPresentationTime: CMSampleBufferGetPresentationTimeStamp(sample)) { fail("Append: \(String(describing: writer.error))") }
   count += 1
  }
  if reader.status == .completed { break }
 }
}
done.wait()
if writer.status != .completed { fail("Encode: \(String(describing: writer.error))") }
print("frames=\(count) elapsed=\(Date().timeIntervalSince(start))")
