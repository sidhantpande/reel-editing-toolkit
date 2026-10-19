# Reel editing toolkit

Reusable, filesystem-first editing environment for ATFRO, NioLearn and My Dental & Skin Clinic. The step-by-step, multi-brand entry point is [EDITING_PIPELINE.md](docs/EDITING_PIPELINE.md). Clinic style and source-aware rendering live in [the clinic workspace](workspaces/my-dental-skin-clinic/README.md). Start with [AGENTS.md](AGENTS.md) and [the CLI workflow](docs/AI_WORKFLOW.md). No dashboard/server is needed.

```sh
git lfs pull
bash tools/bootstrap.sh
python3 tools/reelctl.py doctor
python3 tools/reelctl.py assets --query "clock"
python3 tools/reelctl.py scenes --query "interview"
```

The kit contains 156 checksum-indexed assets, 42 native motion scene kinds, transparent B-roll clips, original music/SFX, fonts/licences, logos, caption/transition code, dependency locks and reviewed edit decisions. See [the asset index](catalog/ASSET_INDEX.md), [approved style](docs/PREMIUM_STYLE.md) and [reference analysis](docs/REFERENCE_ANALYSIS.md).

```sh
python3 tools/reelctl.py init --brand niolearn --id niolearn-next-topic --source /absolute/main.mov
# Analyse the complete source, then fill the reviewed cut/word/editorial JSON.
python3 tools/reelctl.py preflight projects/niolearn/niolearn-next-topic
python3 tools/reelctl.py render projects/niolearn/niolearn-next-topic
```

[Templates](templates/ai-edit/) document the edit contract. Historical `projects/` retain real reviewed cuts, source word timings, scripts, provenance and QA for reuse. New recordings must be supplied each time. Raw recordings, supplied reference videos and all rendered final/client videos are excluded from Git and were authorized for local removal by the owner on 16 October 2026. Historical export/footage indexes describe the earlier batch, not files included in this repository.

```sh
npm test
npm run check
python3 tools/git_audit.py
```

Portable checks run without old camera files. `npm run check:media` additionally requires every historical source recording. Rendering a specific project always checks that project's source media. Remotion Studio is an optional composition preview via `npm run studio`.

Current reliable renderer: 1080×1920 / 30 fps, serial PNG capture, software GL and separate encoding. Preserve these settings unless encoded frames have been verified after a change. The runtime, model caches and virtual environments install locally; they are restored from version locks rather than stored in Git.

Repository: [sidhantpande/reel-editing-toolkit](https://github.com/sidhantpande/reel-editing-toolkit). Binary original assets use Git LFS. Third-party code/fonts retain attribution and licences; Remotion use is subject to its [included licence](docs/licenses/Remotion-LICENSE.md).

## Clinic quick start

```sh
python3 tools/pipeline.py clinic doctor
python3 tools/pipeline.py clinic status
python3 tools/pipeline.py clinic assets
```

The user-approved clinic baseline is Reel-07 v05: transparent top-left logo, compact Mukta/Montserrat word captions and short dissolves. Approved user-supplied B-roll MP4s are backed up through Git LFS; camera recordings, reference reels, final exports and caches remain local. See the [clinic style guide](workspaces/my-dental-skin-clinic/docs/APPROVED_STYLE.md).

## Jet Kids event footage and Log conversion

Jet Kids has a separate [event workspace](workspaces/jetkids/README.md), [reference breakdown](workspaces/jetkids/docs/REFERENCE_ANALYSIS.md) and [audio record](workspaces/jetkids/docs/AUDIO.md). The reusable [colour workflow](docs/COLOUR_WORKFLOW.md) identifies Sony gamma/gamut from XML before applying an official Sony LUT. Use `python3 tools/pipeline.py jetkids status`, `jetkids colour --backend metal`, or `jetkids analyse`. Originals, conversions, reference audio and review images stay local.

## Music intake, beat markers and event edits

`python3 tools/music_assets.py fetch` downloads the17 user-selected exact links, trims48kHz sample-accurate PCM masters and produces320kbps MP3 assets with source/channel/hash/loudness metadata. `music_assets.py audit --require-pcm` verifies checksums, decoded sample counts and beat provenance. Beat/onset CSVs and Premiere-compatible FCP7 marker XMLs distinguish user cues from estimated beats. See [MUSIC_AND_BEATS.md](docs/MUSIC_AND_BEATS.md).

Jet Kids is now in a [four-reel restart review](workspaces/jetkids/docs/RESTART_REVIEW.md), with both landscape and portrait planned. The earlier50s overview previews were rejected by the user. `pipeline.py jetkids preflight|render PLAN` checks source handles before serial transitions; `event_qa.py` scans encoded frames and exports boundary contacts. Selected music MP3 excerpts use Git LFS as explicitly requested; full songs, raw footage, PCM masters, reference media and final exports stay local.
