// Local framing evidence only. Does not identify people or select speakers.
import Foundation
import Vision
import CoreImage
var rows:[[String:Any]] = []
for path in CommandLine.arguments.dropFirst() {
    try autoreleasepool {
        let request=VNDetectFaceRectanglesRequest()
        let handler=VNImageRequestHandler(url:URL(fileURLWithPath:path),options:[:])
        try handler.perform([request])
        let faces=(request.results ?? []).map { f -> [String:Double] in
            let b=f.boundingBox
            return ["x":b.minX,"y":1-b.maxY,"width":b.width,"height":b.height,"confidence":Double(f.confidence)]
        }
        rows.append(["path":path,"faces":faces])
    }
}
let data=try JSONSerialization.data(withJSONObject:rows,options:[.sortedKeys])
FileHandle.standardOutput.write(data)
