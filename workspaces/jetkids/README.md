# Jet Kids event workspace

**Current stage: all475 clips analysed and345 Log masters verified;17 selected soundtracks extracted/indexed. The requested50-second overview review draft is produced. Other reels remain for individual edits.**

**Eventual delivery format: 1920×1080 landscape, 30 fps. Video footage only between shots; no event-photo inserts.** The user changed from portrait after discussing the framing limitations.

Event source: `/Users/shwetaranjan/Pictures/OCT18-PIXON`.

The inventory includes 470 Sony MP4s under Videos plus five Nikon MOVs under Photos: 475 clips, 55 minutes 36 seconds, about 45.5 GiB. Existing source XML identifies Sony ILCE-7M4 (A7 IV) and ILCE-7RM5 (A7R V).

Activate this machine's local runtime first:

```sh
source .cache/setup/activate.sh
python3 tools/pipeline.py jetkids status
python3 tools/pipeline.py jetkids doctor
```

Reusable colour and analysis commands:

```sh
python3 tools/log_colour.py download-lut
python3 tools/log_colour.py inventory /absolute/event/folder --out .cache/jetkids/inventory.json
python3 tools/log_colour.py convert .cache/jetkids/inventory.json --output media/colour/jetkids-rec709 --backend metal
python3 tools/event_review.py .cache/jetkids/inventory.json --conversions media/colour/jetkids-rec709 --out .cache/jetkids/analysis
```

`metal` uses Apple's local Core Image/AVFoundation pipeline and the exact downloaded Sony cube. Its source is `tools/sony_colour_metal.swift`; Swift compiles into ignored `.cache/bin`. `--backend ffmpeg` uses high precision tetrahedral LUT interpolation and a native-frame-rate FFmpeg path. Neither backend touches original footage. The state manifest records completed full-decode/frame/audio checks; visual review is separate.

The reference manifest maps all three supplied files and extracted original audio. The supplied logo is preserved under `public/assets/brands/jetkids/`. Plans and review decisions are text; media, conversions, extracted audio and caches remain ignored.

See [colour workflow](../../docs/COLOUR_WORKFLOW.md), [reference analysis](docs/REFERENCE_ANALYSIS.md), and [audio policy](docs/AUDIO.md).

## Current deliverable

Conversion is complete:345 verified Rec.709 masters, with125 Sony display-referred and5 Nikon videos retained without Sony Log LUT. All475 originals passed a second SHA-256 audit. Full-span sampled visual review covers475 videos across36 survey pages (3997 sample images including exact final frames). This is sampled visual analysis, not every-frame playback or verified listening.

Read the [complete reel plan](docs/REEL_PLAN.md):17 distinct concepts plus8 derived short/extended versions, with source pools, approximate candidate windows, story order and later audio direction. [Source index](source-index.json), [clip notes](clip-review.json), [editable plan](reel-plan.json) and [review status](review-status.json) retain the evidence. The requested overview review edit is `exports/jetkids-overview-v03.mp4`; see `edits/04-overview-v03/production-plan.md`. Final listening/review approval is not claimed. Other reels remain for individual edits.

Latest comparison pair: `exports/jetkids-overview-v03.mp4` (1920×1080) and `exports/jetkids-overview-portrait-v02.mp4` (1080×1920),50s/1500frames each. Portrait uses per-shot crop/follow plus moving-video fit for essential groups; no event-photo inserts. Audio is byte-copied from the finished landscape mix and decoded-audio hashes match. Neither is claimed listening-approved final.
