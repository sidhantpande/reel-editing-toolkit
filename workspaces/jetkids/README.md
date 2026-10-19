# Jet Kids event workspace

**Restart: four reels only, each eventually in landscape and portrait. Current work is source/audio re-analysis; further user downloads are pending.**

All earlier overview previews are rejected historical drafts. The old 17-concept plan, soundtrack assignments and portrait fit-video treatment are superseded. Read [the current brief](AGENTS.md) and [restart findings](docs/RESTART_REVIEW.md). New source volume: `/Volumes/Sidhant-0`; earlier source: `/Users/shwetaranjan/Pictures/OCT18-PIXON`.

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

## Historical work and restart evidence

Earlier technical conversion produced345 verified Sony Rec.709 masters. The125 display-referred Sony sources remain untransformed. Five historical Nikon MOV paths are currently absent. Previous sampled survey notes are retained for comparison; they are not approval of the rejected edit choices.

The old17-concept plan and all landscape/portrait preview versions are superseded by the four-reel restart. The fit-video portrait treatment is rejected. See [restart findings](docs/RESTART_REVIEW.md) for current source pools and review limitations. The local mapping workbook is `exports/jetkids-restart-review/jetkids-footage-mapping.xlsx`; raw interviews, draft transcripts and caches stay local.
