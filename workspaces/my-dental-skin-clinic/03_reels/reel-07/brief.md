# Reel 07 — Kaalratri / missing-tooth options

Latest status: v05 cue-cleaned dissolve edit. Export: 05_exports/review/reel-07_clean-dissolves_v05.mp4; 48.2 seconds, 1080×1920 / 30 fps. Removed the three off-camera production cue runs from 0093, 0096 and 0097, and the incorrect “तो” caption forced over the closing cue. Independent short English ASR identified the opening “Start”; isolated body/closing snippets were decoded as start/stop commands, corroborating the user’s feedback. Output boundary ASR now begins with Kaalratri, “one option is implant” and “which best”, respectively. See v05/cue-asr-audit.json and clean-boundary-asr.json. Exact source exclusions and remapped captions are in v05/plan.json.

Thirteen six-frame picture dissolves use source handles; speech slices retain exact timing without overlapping syllables. Received implant and bridge footage covers the visually identified screen-reading portions; B-roll has seven-frame alpha dissolves. No “3D illustration” label. Logo remains top-left; compact Mukta/Montserrat animated word captions retained. Full export decode passed; audio and video both 48.2 s. Gaze contact sheets, transition frame strips and export board inspected. Direct listening is unavailable in this session; this remains a review export, with source/cue decisions and independent ASR checks recorded transparently.

The original A-roll preparation notes below are retained for context.

Six clips were registered, inspected through contact sheets, and transcribed locally. The user has no written script. ASR produced spelling errors and repetitions, especially on 0094–0095. A normalized Hindi second pass corroborated the general message in 0093 and 0096, but failed elsewhere. Neither transcript is approved subtitles. Direct audio listening is unavailable to the agent in this session; exact wording and word-level final cuts remain unverified. The review contains section labels, not final verbatim captions.

## Source arrangement

| Ending | Role | Decision |
|---|---|---|
| 0092 | Alternate opening with setup chatter | Alternate |
| 0093 | Kaalratri, fear and missing-tooth opening | Selected opening |
| 0094 | Implant pickup | Alternate; ASR unreliable, not necessarily unusable footage |
| 0095 | Short pickup | Alternate; ASR unreliable |
| 0096 | Implant, bridge, removable options | Selected body |
| 0097 | Clinical-condition closing | Selected closing |

01_selected_sources/ and 02_alternate_sources/ contain readable symlinks to untouched originals. Exact source/timeline ranges: 04_timeline/selects.csv and edit-plan.json.

## Editing direction

- Keep Kaalratri opening, missing-tooth problem, implant, bridge, removable-option qualification, then clinical-condition closing.
- Later clips need top-wall removal; closer portrait crops are saved in the edit plan.
- Sources: 1728×3072, 59.94 fps, SDR HEVC, 48 kHz stereo AAC. Review: 1080×1920, 30 fps, H.264/AAC.
- Channels are identical; no phase cancellation found. Audio is quiet (roughly −34 to −38 dB RMS). Review applies 70 Hz high-pass and loudness normalization. Avoid heavy denoising without listening.
- Supplied brand: My Dental Clinic. Logo accent #B36246, charcoal #20201E, warm white #FFF9F2. Manrope ExtraBold for English/Hinglish; Noto Sans Devanagari Bold for Hindi.
- Original logo is 225×225: avoid large enlargement. 06_brand/style-preview.png demonstrates logo and caption direction on footage.
- Full caption spelling, timing, dialogue cut boundaries and final playback require audio review. Do not label this export final.

## B-roll slots

| Request | Section | Draft timeline | Source time in 0096 | Return filename |
|---|---|---|---|---|
| B01 | Implant support | 00:23.733–00:29.233 | 00:03.200–00:08.700 | reel-07_B01_implant_v01.mp4 |
| B02 | Bridge support | 00:33.417–00:38.917 | 00:13.300–00:18.800 | reel-07_B02_bridge_v01.mp4 |

Placement may shift during pacing review. Retain doctor audio under B-roll. Keep removable-option qualification and clinical-condition closing on camera. The user explicitly rejected the “3D illustration” label on 2026-10-17; omit it from all subsequent edits.

Copy-ready prompts: 05_broll_requests/prompts.md. User generates the clips. Check returned anatomy, supports and visual consistency before insertion. No invented patient before/after or treatment success claim.

## After delivery

1. Review both generated clips and insert the best 4–5.5 seconds.
2. Verify spoken wording and cut boundaries through playback; finish phrase captions and branding.
3. Check colour, intelligibility, caption safe areas and full export playback before final delivery.
