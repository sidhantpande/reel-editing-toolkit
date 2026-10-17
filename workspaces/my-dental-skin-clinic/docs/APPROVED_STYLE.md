# My Dental & Skin Clinic — approved edit style

Baseline: Reel-07 **v05**, approved by the user on 17 October 2026. Reference export is local: `05_exports/review/reel-07_clean-dissolves_v05.mp4`. Earlier versions are history, not the default look. Apply this style to Reel-08 and subsequent clinic reels unless the user changes it.

## Picture, logo and finishing

- Vertical 1080 × 1920, 30 fps, natural SDR colour. Source DJI footage is 1728 × 3072 at 59.94 fps; decode before producing 30 fps edits.
- Use the supplied transparent **My Dental Clinic** mark at **x=65, y=65**, width 255 px. The workspace name includes “Skin”; the actual supplied logo says “My Dental Clinic”. Do not invent a different logo/name lockup.
- Logo crop from transparent 1774 × 887 asset: x=162, y=230, width=1460, height=468; scale to 255 px wide. A subtle white glyph halo aids readability; no white rectangle.
- Face/gesture crop must be checked per source. Reel-07 opening used x270/y520/w1188/h2112; later takes x249/y1344/w972/h1728. These are examples, **not universal crop coordinates**.
- Natural correction baseline: contrast 1.025, brightness +0.003, saturation 1.02. Soft lower black gradient begins around y1020 and reaches alpha145 at the bottom.
- H.264, yuv420p, CRF18, fast preset, AAC192k/48k stereo, MP4 faststart. No added music/SFX has been approved for this baseline.

## Dialogue and shot selection — mandatory editorial pass

1. Identify actual take starts/stops independently of silence detection. In Reel-07, automatic Hindi ASR omitted three off-camera “Start” commands and forced alignment stretched intended script words across those cues. **ASR/VAD/forced alignment cannot decide editorial content on their own.**
2. Inspect every source's beginning, middle/pickup boundaries and ending for production commands, false starts, repeated lines and screen-reading pauses. Transcribe isolated suspicious snippets without an intended-script prompt; a second language pass may expose English commands.
3. Keep complete words/phonemes and the speaker's qualifications. Trim excess silence, setup chatter and unusable attempts. Preserve short natural breath pauses.
4. Remove silent screen glances. If the doctor is speaking while reading off-camera, cover the necessary portion with an appropriate supplied B-roll shot; keep the narration. Do not fabricate eye contact.
5. Use **short dissolves** at visible picture joins: baseline six frames / 0.20 s. Decode three frames of source handles on either side, rather than freezing faces or overlapping spoken words. B-roll uses approximately seven-frame / 0.23 s alpha fades. Review every join; avoid long double-face ghosting, black flashes and elaborate transitions.
6. Build dialogue from exact 48 kHz PCM source slices. Apply six-ms edge fades for click prevention. Do not concatenate separately AAC-encoded speech runs: encoder padding previously caused drift.
7. Audio finishing: high-pass70 Hz and loudnorm I=-16, TP=-1.5, LRA11. Measure the encoded result; these are processing targets, not a guarantee of measured loudness.

## Captions — the approved font and motion system

- Hindi: **Mukta ExtraBold**. English: **Montserrat ExtraBold**, static weight800 instance named Clinic Montserrat. Font sources, copyright and SIL OFL licences are retained in `assets/fonts/`.
- Short, meaningful groups with progressive **word-by-word entrances**. Words keep their final positions as the group builds. Keep clinical names/spellings under review until checked against speech; never invent dialogue.
- White normal words; warm yellow `#FFF03A` important words. Important English terms are uppercase. Vary sizes purposefully; do not make every word equally huge.
- At 1080 px width: Hindi normal80/key90/emphasis100, connector68 px. English normal94/key104/emphasis118 px. Balance at most two rows; scale a row only when needed to stay within an870 px text width.
- **Measure visible glyph ink with the same Pillow/RAQM font used to draw it**. Final ink-to-ink gap11 px, line gap12 px. This fixes the large gaps caused by mixing libass and Pillow font metrics.
- Caption centre around x510 / y1328; lower alpha movie is1080 ×620 composited at y1100. Maintain right-side platform UI clearance. Recheck actual Devanagari shaping and text bounds.
- A2 px dark outline and soft shadow keep white text readable. No large caption boxes.
- Entry opacity28 ms, exit40 ms. Scale normal words .93→1.02→1; emphasized words .87→1.045→1. Peak around95 ms, settle around175 ms. Reveal words near their spoken starts; preserve tight, comfortable spacing and fixed baselines.
- The retained implementation is `tools/render_reel07_v04.py::captions`; the approved edit assembly is v05. New reels use a data-driven plan and the shared clinic renderer.

## B-roll and wording

- User generates new B-roll. Supply **one or two** specific prompts per reel, tied to exact source dialogue and duration, with predictable filenames.
- Use returned clips only after inspecting their subject, anatomy, continuity, watermark/text and duration. Discard their audio; doctor narration continues.
- Reel-07 user-supplied implant and bridge assets are approved for reuse where the topic fits. Their provenance is user supplied; the downloaded bridge file's third-party licensing is unverified. A private backup is not a stock-media licence.
- The user explicitly rejected the **“3D illustration” label**. Do not add it, generator prompts, placeholders or production notes to the video.
- Do not add treatment promises, testimonials, invented outcomes, clinic contact details or medical claims beyond the supplied speech. Keep qualifications intact.

## Review and acceptance

Check all source cue boundaries, complete dialogue, captions and glyph spacing, gaze coverage, every dissolve/B-roll boundary, logo position and the final encoded export. Full-decode the MP4 and compare exact audio/video durations and frame count. Record actual checks and limitations; ASR-only checks do not constitute human listening. Preserve earlier exports and source originals. Save QA and edit decisions per reel; only the user's approval promotes a style revision.
