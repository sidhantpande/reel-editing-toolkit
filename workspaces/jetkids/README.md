# Jet Kids event workspace

**Current brief: four mandatory event reels plus additional interview-led stories, each eventually in landscape and portrait. Current work is the arrival-led overview revision02 in landscape and portrait, using the two latest user-supplied audio mixes. Full interview transcription/review and in-depth talking-head edits with relevant B-roll follow the overview.**

All earlier overview previews are rejected historical drafts. The old 17-concept plan, soundtrack assignments and portrait fit-video treatment are superseded. Read [the current brief](AGENTS.md) and [restart findings](docs/RESTART_REVIEW.md). New source volumes: `/Volumes/SID-SSD` and `/Volumes/Sidhant-0`; earlier source: `/Users/shwetaranjan/Pictures/OCT18-PIXON`.

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

The old17-concept plan and all landscape/portrait preview versions are superseded by the current source-led restart. The fit-video portrait treatment is rejected. See [restart findings](docs/RESTART_REVIEW.md) for current source pools and review limitations. The local mapping workbook is `exports/jetkids-restart-review/jetkids-footage-mapping.xlsx`; raw interviews, draft transcripts and caches stay local.

## Current story mapping

The four mandatory sports-event stories and additional interview-led research are in [INTERVIEW_STORY_MAP.md](docs/INTERVIEW_STORY_MAP.md). SID-SSD was inventoried:65 existing sports-source matches and75 entries from a separate evening event. The user asked to park the evening material in [its own workspace](../jetkids-evening-event/README.md). The local workbook now has eight tabs, including interview contributions, selected-action research and the SID-SSD event assignment ledger. Draft times are not approved cut points.

## Current overview revision

See [arrival-led revision02](edits/07-overview-delivery-v01/production-plan.md). The first supplied new reference supplies diya/continuation music; the second supplies entry music. Earlier arrival-flow and overview rebuild exports are rejected history. Optional [neural beat analysis](../../docs/NEURAL_BEAT_ANALYSIS.md) and [subject tracking](../../docs/SUBJECT_TRACKING.md) run in isolated local environments. Raw/reference media, transcripts, models and exports remain local. Sony originals are now on HP USB20FD; the five historical Nikon MOVs were found on SECRET and their full hashes match.

Current delivery settings are saved in `styles/event-cinematic.json`. Original/master speed evidence is in `edits/07-overview-delivery-v01/native-speed-audit.json`.30fps is delivery; native camera frame rates remain in the masters. The current overview is a review revision, pending user response. Full interview-led edits remain the next commissioned phase.
