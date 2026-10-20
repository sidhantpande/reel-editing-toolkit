# Local interview research

The approved Jet Kids overview is locked. Interview research is a separate stage: inspect full-span source contacts, transcribe the full source audio in its spoken language, group speakers and retakes, then plan complete thoughts with matching real B-roll. A short prepared school explainer is different from an event reaction. Keep the separate evening event separate.

## Installed transcription tools

The current Mac uses [whisper.cpp](https://github.com/ggml-org/whisper.cpp) at commit `231638a0717b7822784297e5980965ffcec05810`, built with Metal, and the [large-v3-turbo q8 model](https://huggingface.co/ggerganov/whisper.cpp). The exact model revision, checksum and decoding configuration are saved in [the project toolchain record](../workspaces/jetkids/interview-toolchain.json). CMake is pinned to3.31.6. Models, third-party checkouts and compiled tools remain in ignored caches.

Existing faster-whisper small research remains a comparison. Tests on this footage exposed repeating Hindi output and language changes between short chunks. A larger model is useful evidence, but it does not certify the words, a speaker's name or a clean sentence boundary. Do not supply an expected script as a transcription prompt. The current native prompt contains only the school/place names.

For a new machine, restore the pinned source commit, install CMake into a local cache, build `whisper-cli` with `-DGGML_METAL=ON`, and fetch the immutable model URL in the toolchain record. Verify its SHA-256 before use. The current CLI is `.cache/tools/whisper-cpp/build/bin/whisper-cli`; an Apple Silicon build needs the platform compiler/SDK. See the upstream build instructions. Do not add caches or model binaries to Git.

## Source audio and ASR

Extract a working16kHz mono WAV from each original without changing its playback rate. Retain the original camera audio and record source ID, path, duration, extracted sample count and hash. Match the extracted duration to the source before transcription. These working WAVs are research inputs, not replacement dialogue masters.

```sh
ffmpeg -i /absolute/source.MP4 -map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le /absolute/research/V001.wav
.cache/tools/whisper-cpp/build/bin/whisper-cli \
  -m .cache/models/whisper-cpp/ggml-large-v3-turbo-q8_0.bin \
  -f /absolute/research/V001.wav -l hi -bs 3 -bo 1 -nf -t 4 -mc 0 \
  -ojf -of /absolute/research/native/V001
```

Use a supported source language (`hi`, `en`, `mr`, or `auto` where uncertain). Language triage and silence/speech detection are research aids, never final edit decisions. Multiple `-f` and matching `-of` arguments allow a serial batch with one model loaded. Inspect the actual output and source; background PA speech, song lyrics, count-ins and camera directions are not interview answers.

## Compile source-aware research

`tools/interview_research.py` compiles native JSON or completed faster-whisper research into local JSON and readable Markdown. It preserves stable source IDs, exposes timing overruns and undecodable bytes, keeps overlapping comparisons, and refuses duplicate IDs or a mismatched full-source audio duration. It never marks captions, cuts or listening approved. Some native JSON token byte fragments are invalid UTF-8; replacements are counted rather than hidden. Token timestamps are not corrected word timings.

The manifest is a list of objects with `id`, `path`, `duration`, and measured `audio_duration`; `event`, `audio_sha256` and working-audio metadata may accompany them. The faster-whisper comparison format uses absolute source-relative seconds within `chunks[].segments[]`. Do not feed a different chunk timing format without converting it explicitly.

```sh
python3 tools/interview_research.py \
  --manifest /absolute/local/audio-manifest.json \
  --native-dir /absolute/local/native \
  --fallback-dir /absolute/local/comparisons \
  --out /absolute/local/research --require-complete
```

The completeness gate accounts for completed full-source ASR **attempts** plus explicitly measured digital silence (`audio_status="silent"` and `peak=0`), not verified recovery of every word. Silent sources receive an empty evidence entry rather than invented transcription. Review each source's actual meaning, question context, repetitions, false starts, speaker role, gestures and image quality. Correct selected speech and align words before creating an edit. Keep full transcripts and client media local.

## Approved version protection

Overview09's recipe refuses a new render once `approval-lock.json` exists; `--preflight` remains available. Create a new version for any requested changes. Verify the approved export bytes with:

```sh
python3 tools/approved_delivery.py workspaces/jetkids/edits/09-reference-led-overview-v01/approval-lock.json
```

Derived overview caches may be removed after preserving the approved exports, original media, recipes and useful QA. A symlink collection is not a backup. The current cleanup record states logical bytes removed separately from filesystem free-space changes.
