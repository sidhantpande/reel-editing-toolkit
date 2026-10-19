# Camera Log to display colour

This stage normalises a known camera gamma/gamut to a display look; it is separate from shot-specific exposure/white-balance matching and the final creative grade. Originals are read-only and conversions stay in ignored `media/colour/`.

## Identify the input first

Read Sony `*M01.XML`: `Device`, `CaptureGammaEquation`, `CaptureColorPrimaries` and `CodingEquations`. Container `bt709` matrix tags alone do not prove a Sony clip is non-Log. Match the video to its own sidecar; an orphan sidecar is not an additional clip.

For OCT18-PIXON, existing source files classify as:

| Camera / evidence | Count | Treatment |
|---|---:|---|
| Sony ILCE-7M4, s-log3-cine / s-gamut3-cine | 345 | Official matching Sony LUT once |
| Sony ILCE-7M4, nxcam-still / rec709 | 4 | No Log LUT |
| Sony ILCE-7RM5, s-cinetone / rec709 | 120 | No Log LUT |
| Sony ILCE-7RM5, rec709 / rec709 | 1 | No Log LUT |
| Five Nikon MOVs within Photos, BT.709 tags | 5 | Preserve, visually assess; no guessed Sony LUT |

A matching XML exists for 470 Sony video files. There is also one unmatched XML, so counting XMLs alone incorrectly gives 346 Log clips. Unknown gamma/gamut must be reviewed; it is never automatically assigned a LUT from appearance alone.

## Official transform and provenance

Sony's [LUT download support article](https://www.sony.com/zh-cn/electronics/support/articles/00197011) links to the [official S-Gamut3.Cine/S-Log3 ZIP](https://di.update.sony.net/NEX/ciOkozszIz/Look_profile_for_resolve_S-Gamut3.cine_Slog3.zip). `tools/log_colour.py download-lut` downloads `SLog3SGamut3.CineToLC-709.cube` into `.cache/luts/sony/` and writes source URL, input/output space and SHA-256 provenance. Sony retains rights; the vendor cube is not redistributed in Git.

The selected cube declares **full in, full out** and a 33-point 3D grid. LC-709 is a Sony display look; it is not a saturation slider or a generic contrast approximation. See [Sony's grading guidance](https://support.d-imaging.sony.co.jp/support/ilc/movie/en/grading/03.html).

FFmpeg path: explicitly interpret the source range and 709 coding matrix, convert to high-precision RGB, apply the actual 3D LUT with tetrahedral interpolation, convert full-range output RGB to limited-range YUV, and tag primaries/transfer/matrix as BT.709. Do not merely change colour tags, apply the LUT twice, or use S-Log2/S-Gamut3 cubes for S-Gamut3.Cine footage.

macOS Metal path: AVFoundation decodes source YUV to BGRA, Core Image uses the same 33³ Sony cube with colour-management spaces disabled to preserve Log code values, and AVFoundation encodes Rec.709 H.264. Native timestamps and source transform are retained. A converted video-only temporary is muxed with the untouched source audio; completed masters are verified before being marked complete. Apple Core Image LUT interpolation differs from FFmpeg tetrahedral interpolation; representative output frames must be compared visually before a new camera/profile batch uses this path. An initial fixed-timestamp source check against FFmpeg showed a mean absolute RGB difference of about 1.8/255; this is a backend check, not a whole-batch grade approval.

## Run and verify

```sh
source .cache/setup/activate.sh
python3 tools/log_colour.py inventory /absolute/source/folder --out .cache/event/inventory.json
python3 tools/log_colour.py convert .cache/event/inventory.json --output media/colour/event-rec709 --backend metal
# Portable alternative with FFmpeg LUT processing:
python3 tools/log_colour.py convert .cache/event/inventory.json --output media/colour/event-rec709-ffmpeg --backend ffmpeg
```

The Metal backend requires macOS, Swift and Metal. The default FFmpeg backend needs `h264_videotoolbox` on this Mac; its command builder also supports libx264 for future platform integration. Outputs preserve source resolution, 100/50/25 fps and duration. MOV allows the camera's PCM stream to be copied without re-encoding. Every completed master undergoes full video/audio decode, matching frame count/duration/fps/dimensions, output colour-tag checks, an unchanged decoded-PCM hash check and a recorded output SHA-256. Resume accepts only the same LUT and source/output hashes. Partial/unverified outputs remain separate and never count as complete. Low disk space stops the batch.

## Visual grade and edit

Inspect converted skin, white clothing, foliage, coloured courts and highlight retention across lighting changes. Balance exposure and white balance before/around the technical transform as required by the shot; do not add an arbitrary global yellow/red/blue tint. Match the already display-referred A7R V camera to the chosen neutral baseline after normalisation, without applying a Log LUT to it.

Source Log video is already 8-bit. Clipped whites, blown exposure, focus errors or banding cannot be recovered by calling the conversion perfect. Mark damaged shots, prefer good alternate takes, and inspect the selected encoded reel after final correction. Technical batch completion does not attest to a human/model having reviewed every full-resolution frame or listened to every source clip.
