# Music assets, beat cues and smooth event transitions

Use the project's exact watch URL and an explicit source slice. A Google/YouTube search URL is discovery, not an audio asset. Jet Kids'17 user-selected URLs and original structural cues are in `workspaces/jetkids/music-cues.json`. The manifest preserves requested song, concept, upload ID/title/channel/date, source slice, hashes, PCM sample count, codec, MP3 bitrate, measured loudness and rights/permission context.

## Repeatable intake

```sh
source .cache/setup/activate.sh
python3 tools/pipeline.py jetkids music fetch --reel 04
python3 tools/music_assets.py fetch                 # all17, bounded two-worker downloads
python3 tools/music_assets.py audit --require-pcm
python3 tools/music_assets.py export-markers
python3 tools/catalog.py
python3 tools/reelctl.py assets --brand jetkids --kind music --query Ilahi
```

`tools/bootstrap.sh` installs `requirements.lock` and `requirements.audio.lock`. The audio extension pins yt-dlp, its EJS companion and librosa/scipy dependencies. Node22+ is the YouTube JavaScript runtime. FFmpeg handles sample trimming/MP3 conversion; no Premiere installation is required to prepare assets. No cookies, browser sessions or credentials are read by the downloader. Failed requests are recorded separately and never relabelled as successful assets.

Full audio downloads and source-info caches stay under ignored `media/music/jetkids/ID/`. The trim origin is the first decoded PCM sample: normalise codec PTS, resample48kHz and trim exact sample indices. This avoids the7.5ms Opus start-offset deficit seen in this batch. A50s slice has2,400,000 samples per channel. Missing audio is never silently padded. PCM edit masters remain24-bit WAV locally; shareable320kbps MP3 slices under `public/assets/brands/jetkids/audio/` use Git LFS. MP3 decoded sample counts, not rounded container durations, are audited.

The user explicitly authorised pushing these selected excerpts after being told that the GitHub repository is public. This is a permission record for the requested backup, not a claim that commercial recordings are royalty-free or that a music licence has been issued. Full songs, raw/reference footage and final client exports remain excluded from Git.

## Timebases and marker exports

Source-song seconds and trimmed-reel seconds are different. `timeline_seconds = source_seconds − source_in`; `timeline_frame = round(timeline_seconds ×30)`. For reel04, source52s minus slice start35s gives reel17s/frame510. Source70s becomes reel35s/frame1050. Store this conversion rather than pasting absolute song times onto a trimmed sequence.

`workspaces/jetkids/beats/` contains JSON and CSV for each excerpt. HPSS isolates a percussive analysis signal; librosa estimates an onset envelope, tempo and beat candidates using dynamic programming. These are **estimates**, not verified lyrics, chorus/downbeat labels or proof of listening. The user's structural markers retain a separate unverified musical-status field. A candidate rounding to the first frame beyond the slice is excluded.

`premiere-markers/ID.xml` is an FCP7 XML audio sequence with linked stereo channels,30fps rate, source MP3 reference and sequence markers. It includes USER CUE and AUTO BEAT prefixes. Files are XML/stereo/frame-bound validated; actual Premiere GUI import was not performed here. Relink the MP3 when importing on a different machine. The CSVs remain a portable alternative. Do not describe these whole-second structural cues as a measured frame-by-frame beat map.

Use `tools/beat_sync.py PLAN BEAT_JSON` to audit structural cut-frame alignment. Its reusable `snap()` only moves a boundary when a beat is within a specified frame radius; `action_in()` computes the source start needed to place a reviewed bat/ribbon/gesture frame at a chosen timeline marker, accounting for slow motion. Ball contact and human gestures still require visual source inspection.

## Transition assets and rendering

Eight MIT GLSL sources were downloaded from [GL Transitions](https://github.com/gl-transitions/gl-transitions), pinned to commit/hash in `catalog/event-transitions.json`, with upstream authors and LICENSE retained in `vendor/gl-transitions/`. They are reusable source assets; this does not claim every shader was compiled or used in the current video.

The active event renderer uses FFmpeg's installed effects through `tools/event_transitions.py`. Clean hard cuts carry sports rhythm; restrained6-frame fades carry venue/ceremony/reactions. Fade/fadeslow, smooth directional, hblur and zoomin are supported selections; the actual overview uses clean cuts and fades. Avoid applying a dramatic effect at every beat.

A transition uses real additional outgoing source handles, overlaps those handles with the start of the incoming shot, then retains the incoming core. The overlap cancels the extra handle exactly: a6-frame seam does not remove6frames from the planned timeline. Preflight rejects insufficient handles, an incoming transition on the first shot, unsupported presets, source overruns and invalid slow motion. Seam/core rendering is serial to bound memory. Regression coverage checks frame totals and a decoded colour seam for unexpected dark frames.

```sh
python3 tools/pipeline.py jetkids preflight workspaces/jetkids/edits/04-overview-v03/plan.json
python3 tools/pipeline.py jetkids render workspaces/jetkids/edits/04-overview-v03/plan.json --output exports/jetkids-overview-v03.mp4
python3 tools/event_qa.py exports/jetkids-overview-v03.mp4 workspaces/jetkids/edits/04-overview-v03/plan.json --out .cache/jetkids/overview-v02-qa
```

Use new versioned IDs/output filenames for revisions. The50s overview is a review draft, with1500 encoded frames and a2s original-logo ending. Source-handle seams preserve requested chapter frames510 and1050. Two-pass loudness and encoded true peak are measured; contact sheets cover the full span and every cut. Numeric scans do not replace visual inspection or audio listening. Only attest review actually completed.

Primary technical references: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [librosa beat tracker](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html). Asset/marker manifests record the actual source links used for this batch.

## Portrait companion preview

The user additionally requested one9:16 comparison. `tools/portrait_preview.py` reuses the checked landscape source segments and timing, applying a separate per-shot layout before the same handle seams. Individual subjects receive calibrated/full-height or moving crops. Ribbon/groups retain a full moving-video foreground over blurred moving source background; sign/tilak use larger bounded source windows. No event photos are inserted. The crest is rendered from the unmodified original on black. The50s portrait AAC is copied from its landscape companion and decoded-audio hashes must match.

```sh
python3 tools/portrait_preview.py workspaces/jetkids/edits/04-overview-v03/plan.json workspaces/jetkids/edits/04-overview-v03/portrait-layout-v02.json --landscape exports/jetkids-overview-v03.mp4 --output exports/jetkids-overview-portrait-v02.mp4
```

This is a ratio comparison, not a blanket switch of all17 plans. Native1080 landscape crops require upscaling, and essential group shots remain wider inside the portrait canvas.
