# Jet Kids event workspace

**Overview09 is approved and locked in both landscape and portrait.** Verified export hashes and the user's approval are recorded in [approval-lock.json](edits/09-reference-led-overview-v01/approval-lock.json). Keep this version unchanged.

Current work: full interview research across Downloads/JKIS, mounted HP USB20FD, SECRET, SID-SSD, Sidhant-0 and relevant workspace media. Each cabin guest gets an individual story with captions and real matching B-roll. Parents, teachers and students may also form coherent thematic stories. Retakes and continuation files are grouped by speaker/context. The separate evening event remains separate. The old17-concept plan and old music assignments are superseded.

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

Earlier technical conversion produced345 verified Sony Rec.709 masters. The125 display-referred Sony sources remain untransformed. Five historical Nikon MOVs were reconnected on SECRET with matching original SHA-256 hashes. Previous sampled survey notes are retained for comparison; they are not approval of the rejected edit choices.

The old17-concept plan and all landscape/portrait preview versions are superseded by the current source-led restart. The fit-video portrait treatment is rejected. See [restart findings](docs/RESTART_REVIEW.md) for current source pools and review limitations. The local mapping workbook is `exports/jetkids-restart-review/jetkids-footage-mapping.xlsx`; raw interviews, draft transcripts and caches stay local.

## Current story mapping

The four mandatory sports-event stories and additional interview-led research are in [INTERVIEW_STORY_MAP.md](docs/INTERVIEW_STORY_MAP.md). SID-SSD was inventoried:65 existing sports-source matches and75 entries from a separate evening event. The user asked to park the evening material in [its own workspace](../jetkids-evening-event/README.md). The older eight-tab restart workbook is historical. The current six-tab interview master is `exports/jetkids-interview-research/outputs/session-20261020/jetkids-interview-master.xlsx`, with170 candidate treatments, seven individual profiles,53 quote research windows,32 B-roll candidates and source coverage. Draft times are not approved cut points.

## Locked overview and next stage

The approved [version09 project](edits/09-reference-led-overview-v01/production-plan.md) retains the existing original-speed entry/diya soundtrack. The later132.96s supplied video was visual guidance only; no picture or audio from it appears in the approved overview. Both exports run76.333s at30fps. Original camera/master frame rates are preserved; [native-speed evidence](edits/08-overview-polish-v01/native-speed-audit.json) distinguishes capture fps from delivery fps.

[Cleanup evidence](edits/09-reference-led-overview-v01/cache-cleanup.json) lists removed derived overview caches and retained QA. Original footage, final exports, interview research, source surveys and reusable dependencies remain local. Optional [neural beat analysis](../../docs/NEURAL_BEAT_ANALYSIS.md) and [subject tracking](../../docs/SUBJECT_TRACKING.md) remain available for future work.

Current interview deliverables live locally under `exports/jetkids-interview-research/`; working evidence remains under `.cache/jetkids/interview-deep-review/`.169 full-source ASR attempts plus one measured-silent source account for all170 candidates. The plan prioritises seven individual profiles and four complementary mixed stories while keeping four core event reels and a later principal explainer series distinct. Original-language ASR drafts and review contacts are evidence for planning, not approved captions or an attestation of complete listening. Full raw transcripts and client exports stay out of Git.

See [the local interview workflow](../../docs/INTERVIEW_RESEARCH.md) for the installed/pinned transcription tools, source-aware research compiler and executable approved-export verification. The [interview editorial proposal](styles/interview-editorial-proposal.json) saves the next-stage caption, audio and B-roll direction separately from the approved overview settings.
