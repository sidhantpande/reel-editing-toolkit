# Reference and event audio

Latest direction:17 user-selected song excerpts now supersede the earlier reference-mix defaults. Read [the audio/beat workflow](../../../docs/MUSIC_AND_BEATS.md), [music-cues.json](../music-cues.json) and [music-assets.json](../music-assets.json). MP3 excerpts are explicitly authorised Git LFS assets; full downloads/PCM masters stay local. All slices passed decoded sample-count/checksum audits. CSV/JSON beats are estimates; Premiere-compatible marker XMLs distinguish USER CUE from AUTO BEAT. Actual audio listening and Premiere GUI import are not attested.


The user explicitly asked to reuse the supplied reference reels' audio. All three source mixes were extracted with `-vn -c:a copy`, without re-encoding. Paths and source SHA-256 values are in `../reference-manifest.json`; measurements are in `../reference-audio-analysis.json`.

| Reference | Extracted mix | Intended association |
|---|---|---|
| ref-01 | `.cache/jetkids/references/ref-01/reference-audio.m4a` | VIP arrival / ribbon cutting / launch highlight |
| ref-02 | `.cache/jetkids/references/ref-02/reference-audio.m4a` | Ceremonial opening / lamp / hospitality / event story |
| ref-03 | `.cache/jetkids/references/ref-03/reference-audio.m4a` | Jet Kids campus-to-sports recap |

These are supplied finished mixes, not isolated music stems. Embedded crowd/voice/SFX cannot be claimed absent. Preserve each association and record exact trim offsets when cutting the eventual reel. No YouTube download is necessary for these three mandatory references.

Converted source masters copy original source audio and compare decoded PCM hashes. Final edits should retain purposeful natural details (scissors/ribbon, applause, drum welcome, ball contact, cheering) beneath the reference mix. Do not fabricate live sound from unrelated footage. Music can be ducked under real speech; do not add captions to unclear chatter or invent dialogue.

Measure integrated loudness/true peak on each final encoded reel. Aim for approximately -14 LUFS and at most -1 dBTP, but do not flatten all transients or apply a second loudness pass to raw masters. `reference-audio-analysis.json` contains measured starting values and waveform onset candidates; those onset timestamps need musical review before beat edits.

Audio inspection status must distinguish extraction, waveform/ASR analysis and actual listening. No song identity or listening-complete status is inferred from filenames or waveform measurements. Usage outside this supplied edit should retain the source/permission context; do not describe extracted mixes as royalty-free.

## Source speech screening

A local multilingual Faster Whisper base model also screens long takes and a few student/host gesture clips, with voice activity detection and automatic language detection. Drafts live under `.cache/jetkids/audio-drafts/`. Crowd/music sections produced low-confidence and inconsistent-language output; those words are not accepted dialogue, captions or song identifications. Use them only to locate possible speech for a later listening pass. The reusable `tools/transcribe.py --language auto` now passes automatic detection correctly rather than treating `auto` as a language code.
