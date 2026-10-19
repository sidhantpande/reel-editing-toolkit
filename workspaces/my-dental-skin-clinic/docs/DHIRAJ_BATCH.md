# Dhiraj shoot — clean-cut batch

Initial batch scope: analyse every clip, group actual reels, cut setup/retakes/long silence, frame 9:16, use speaker crops on conversations, and deliver all B-roll requests and visual elements. The user initially chose clean edits with the logo deferred. Branding and B-roll were later supplied: **Reel-01 finish-v04 is now the user-approved caption baseline**, and **Reel-02 finish-v01 is a finished review** using it. All12 reels now have finished review exports;24/24 supplied B-roll requests are received and inserted. Current clean/finish selections are authoritative in active-plans.json and finishing-plans.json. Source footage and earlier exports stay preserved.

Sources: 32 original 4K landscape MP4s (18m19.3s) and 17 JPG reference/cover candidates, left unchanged in `/Users/sidhant/Desktop/Video-Editing/Dhiraj`. Derived exports and handoff: `/Users/sidhant/Desktop/Video-Editing/Dhiraj-Edits/START-HERE.md`. No source, reference or old export deletion is authorised.

## Decisions and evidence

- `03_reels/dhiraj/active-plans.json` selects the current version of each of 12 reels. Do not assume every active plan is v01. Export reel numbers follow this edited batch, independently from script numbers.
- `source-accounting.json` accounts for every MP4, including 12 alternate/setup clips. Source links in the handoff point to unchanged originals.
- `supplied-scripts/` preserves all ten supplied scripts. Actual recordings match scripts 01–06 and 10, with recorded variations. No matching hair-oil, pigmentation, or oily-skin/moisturizer recording was found for supplied scripts 07–09. Extra filmed topics are explicitly labelled.
- Local analysis: complete two-second chronological contacts, three framing candidates per source, draft word timestamps from Faster Whisper turbo, an independent Metal/whisper.cpp pass, and isolated decoding of the passages missed by full-clip ASR. ASR agreement is not a claim of human listening approval.
- Clean dialogue selections are explicit editorial source ranges. The strict silence helper only proposes removal inside these ranges for continuous normalized energy below −44 dBFS for at least 0.9 seconds; 180ms handles stay on both ends. Brief breaths remain.
- Portrait framing is source-specific. Two moving takes use 4fps local Vision face-rectangle evidence and smoothed crop centres. This is framing geometry, not identity recognition. Source-clock crop keys also apply correctly to dissolve handles. Long FFmpeg expressions use a balanced tree to avoid libavutil recursion errors.
- Adult podcast speaker turns follow the actual question/answer/price/thank-you exchange. The separate parent–child conversation has its own crop/turn decisions. No mirrored footage or synthetic faces/voices.

## Tools and regeneration

Use this workspace's pinned `.venv/bin/python` and the full FFmpeg binary from `project.json`.

```sh
.venv/bin/python tools/dhiraj_batch.py analyse
.venv/bin/python tools/dhiraj_batch.py second-pass
.venv/bin/python tools/build_dhiraj_elements.py
.venv/bin/python tools/package_dhiraj.py
```

The Metal second pass uses the existing Homebrew `whisper-cli` plus the checksum/revision-pinned model described in `03_reels/dhiraj/metal-asr-model.json`. It is optional acceleration/independent decoding; the existing Faster Whisper runtime remains available. Weights, audio, face evidence, frames, proxies and exports are local ignored data, not Git assets.

To revise an edit, copy its active plan into a new version folder, set a new `version` and `clean_export` filename, then render that explicit plan. Update `active-plans.json` only to the selected current version. Existing exports are not overwritten when the plan/renderer signature differs.

```sh
.venv/bin/python tools/render_dhiraj_selects.py /absolute/new-version/plan.json
.venv/bin/python tools/qa_clinic_reel.py /absolute/new-version/plan.json \
  /absolute/new-review.mp4 --out /absolute/local-qa-folder
```

Each plan carries source hashes and frame-exact audio/picture ranges. Clean renders use 1080×1920/30fps H.264, original 48kHz dialogue, 6ms audio splice fades and loudness finishing. Six-frame picture dissolves join dialogue; speaker turns use cuts. The parent–child export additionally uses oversampled peak limiting after a measured loud peak was found. No music was added to these clean cuts.

## Transitions, B-roll and elements

`assets/transitions/ffmpeg-n9.0/` contains unmodified official FFmpeg xfade source, its LGPL licence, checksum provenance and a restrained preset set. Runtime transitions use the installed FFmpeg implementation. This is an open-source transition set, not an invented claim that a paid commercial pack was downloaded. Dialogue dissolves and speaker cuts are used in the clean exports; smooth topic/B-roll presets are reserved for actual B-roll insertion.

`broll-requests.json` and `BROLL-PROMPTS.md` contain 24 requests, with retained spoken/source anchors, current timeline placement, motion, exact delivery names and full copy/paste prompts. All24 unique requested clips for Reels01–12 are received and inserted in the selected finished reviews. Reel-02 B02 has two selected insert windows from one supplied asset. Source story changes require recalculating their timeline anchors with the packager.

`assets/cutouts/dhiraj/` contains eight built-in-imagegen illustrations and five original type-card PNGs, with actual alpha, saved prompts, checksums and provenance. The object imagery is generic; no generated patient, child likeness, outcome or new clinical claim. Exact typography uses bundled OFL fonts. Inspect native cards again after regenerating. Assets are copied into the handoff's `visual-elements/`.

Solo-person illustrations may use shot-local matting after encoded edge review. The earlier single-person largest-component matte must not be used to select a speaker in two-person footage. On conversations prefer full-frame inserts or safe cards.

## Reel-01 finishing extension — 19 October 2026

The user supplied `dhiraj_reel-01_B01.mp4`, `dhiraj_reel-01_B02.mp4`, then a wider replacement logo (`images (2).jpeg`). The wider logo is selected in `styles/dhiraj-finishing-v01.json`. Preserve its exact artwork and white background; do not substitute My Dental branding or infer missing letters from the older cropped thumbnail. Originals, approved B-roll copies and logo provenance are checksummed. The delivered B-roll is 720×1280/24fps; convert to the 1080×1920/30fps timeline and discard native audio. Retain the embedded sparkle marks.

`finishing-plans.json` selects finished review plans separately from `active-plans.json`, which continues to select clean cuts. `package_dhiraj.py` preserves finished review links and marks received B-roll shots, rather than resetting every request to pending. The first reel uses B01 at 3.600–8.100s and B02 at 17.433–25.300s; the latter covers the actual peeling line. No extra unrelated cutout or historical clinic outro is added.

```sh
.venv/bin/python tools/finish_dhiraj_reel.py 03_reels/dhiraj/reel-01/04_timeline/finish-v02/plan.json
```

This finishing command verifies the previously checked clean-picture checksum, source hashes, B-roll durations/checksums and selected logo, reuses the original exact PCM dialogue assembly, applies the conservative existing DeepFilterNet3 cleanup, renders curated source-mapped word captions through the shared Mukta/Montserrat engine, and inserts returned B-roll with seven-frame fades. New finished versions use distinct output names. Existing clean cuts and earlier review renders are preserved.

This historical finishing pass used recording/short-decoding support and initially captioned the number as 15; the user later corrected it to **5–10**, which governs the approved v04. The final dermatologist qualification remains. A single unclear English filler decoded as and/end is omitted from the caption while the original voice is unchanged. The recorded procedures passage differs from the supplied script; no additional clinical claim is introduced. Automated speech retention is supporting evidence and does not constitute human listening approval.

## User-requested Reel-01 polish — finish-v03

The user requested quiet background music, improved transitions, removal of the logo's white background, and more varied captions. These requests authorize the changes below and supersede the inherited no-music baseline for this revision. No narration or source timing changes were requested.

- `styles/dhiraj-polish-v02.json` selects the new transparent logo and the phrase-directed caption renderer. `assets/brand/dhiraj/background-removal-prompt.json` contains the exact built-in imagegen edit prompt; `provenance.json` retains the supplied logo and output hashes. Never silently apply a generated reconstruction to a different clinic identity.
- `tools/dhiraj_captions.py` retains shared Mukta/Montserrat glyph shaping and measurement, with explicit per-phrase treatments: enlarged number hook, stacked product lists, restrained question/title underlines, warm caution accents, sage advice blocks, and quieter ordinary clauses. Words still enter at their source-mapped times. Per-phrase rows and typography are saved in `caption_scenes` and `caption-layout.json`; the old clinic caption renderer remains available.
- Direct source picture joins remove the former double-face dissolves. Source cuts remain frame-exact. B01 now runs 3.600–8.300s, covering the short source splice; a 0.30s soft upward reveal and 0.23s exit mask animate the insert. B02 uses a horizontal soft wipe at 17.433–25.300s. Captions and branding remain stable over these picture transitions.
- `tools/dhiraj_audio.py` reuses the original toolkit `calm-focus.wav`, written by `tools/build_assets.py`, with its existing two-second ramps overlapped for continuity. Music targets −31 LUFS before speech-sidechain ducking; sparse quiet `transition-air.wav` cues accompany only the four B-roll boundaries. The full mix is mastered to −16 LUFS / −1.5 dBTP and exact sample count. Record encoded measurement and speech retention; do not claim human listening from loudness or ASR alone.

```sh
.venv/bin/python tools/finish_dhiraj_reel.py 03_reels/dhiraj/reel-01/04_timeline/finish-v03/plan.json
```

## Latest caption revision — finish-v04

The user explicitly corrected the opening number to **5–10 days**, replacing the earlier ASR-derived 15. This human correction governs the current caption and corrected source-word file. Earlier versions remain historical; never restore 15 from their notes or from draft ASR. Narration and music are retained unchanged.

`styles/dhiraj-premium-v03.json` and `tools/dhiraj_premium_captions.py` replace the v03 caption treatment with 47 meaning-led groups containing the same 166 words. Clean white Mukta and Manrope-derived type carries ordinary speech; selected focal English phrases use the licensed Cormorant-derived bold italic and pale gold. Word entrances settle with a short blur/rise; no coloured boxes, embossed outlines or decorative underlines. Text remains source-timed and is measured with the exact rendering font. The range itself reads `5–10` and remains visible at two seconds.

On ivory B-roll, dark ink and bronze focal text replace white lettering, and the caption groups sit below the product imagery. The lower gradient applies to A-roll before inserts, preserving the clean ivory B-roll. Existing B-rolls, transparent logo, source cut timing, music and narration remain selected. New font instancing/provenance is retained at `assets/fonts/ready/dhiraj-serif-provenance.json` under the original SIL OFL licence.

```sh
.venv/bin/python tools/finish_dhiraj_reel.py 03_reels/dhiraj/reel-01/04_timeline/finish-v04/plan.json
```

## Approved batch baseline and Reel-02 — 20 October 2026

The user approved the latest Reel-01 finish-v04 and asked to continue Reel-02, allowing font/layout tweaks. `styles/dhiraj-approved-v01.json` freezes that look for subsequent Dhiraj reels; the earlier clinic brand defaults remain separate. Approval context is saved in `style-approval.json`. The attached `Dhiraj-Sir-R01.mp4` matched an older export, but the user clarified that it was attached accidentally instead of B01; do not treat it as a style rollback.

Both Reel-02 B-rolls are now supplied and checksummed under `04_generated_broll/approved/`: B01 shows the product basket and hand; B02 pans across cleanser, moisturizer and sunscreen. Native audio is discarded and embedded sparkle marks remain. B01 is used on the opening cart/count line. B02 has separate cleanser and moisturizer/sunscreen windows with `request_id: B02`; `package_dhiraj.py` records all selected windows for one returned asset.

Reel-02 clean plan v02 restores leading context before the first question, the address phrase and the final pickup; its direct joins follow the approved finishing style. Duration is now 57.433s / 1723 frames. Old v01 media and plans remain intact. Caption timing follows these current source ranges. The source's third-question wording, gentle-routine explanation and recorded active-product aside remain; no script replacement or added treatment claim. Draft overlaps on जिसके are deduplicated before captions.

The finishing plan is `03_reels/dhiraj/reel-02/04_timeline/finish-v01/plan.json`. Mixed Hindi/English captions use the approved engine, typography and transparent logo, with the same restrained instrumental/ducking profile. Counts 3 and 1 are display equivalents of the spoken तीन and एक; the basket hook retains the recorded 10–10. Independent short decoding supports difficult clauses, while human listening and final wording approval remain explicit review steps.

## Historical clean-cut acceptance evidence

Full MP4 decode, frame counts, 30fps/canvas, A/V duration, black-frame intervals, loudness/peak, every edit boundary, openings/endings, tracked movement, and encoded speech-retention drafts are recorded in the batch QA. Review status remains **clean cuts ready for user review**, not human-approved captions, clinical verification or final branded videos. Recorded wording differences are retained in per-reel notes; do not silently substitute the supplied script or add treatment claims to graphics.

## Reel-03 finishing — 20 October 2026

The user approved Reel-02 finish-v01 and supplied both Reel-03 B-rolls. These 1080×1920/24fps, eight-second originals are checksummed and preserved in the approved asset library with LFS/provenance. B01 is the continuous lemon/turmeric/milk still life; B02 chooses familiar products while a serum stays behind. Native sound is discarded; supplied Veo marks and fictional label-like markings remain. Actual insert windows are 6.400–12.867s (media0.300–6.767s) and 42.333–47.933s (media0.500–6.100s).

Clean v02 restores leading context at four words and keeps the complete closing wish continuous. The finished review uses 161 curated words / 49 meaning-led groups, the approved white/gold type, selective italic English, Dhiraj transparent logo and quiet original instrumental with ducking. Dark ink replaces bronze on the supplied inserts where shadows reduced contrast; the turmeric group sits lower in the quiet foreground. No caption box is added. Current finishing selection is finish-v02; v01 and all clean/original media remain available. Exact duration61.500s /1845frames.

All source/caption/B-roll boundaries, every encoded group, large contrast/framing samples and consecutive word/transition samples are reviewed. Full independent encoded ASR recovers the caution, routine and complete closing; repeated partial decoder lines are decoding artifacts, not timeline duplicates. The v02 audio reuses the same enhanced voice and exact2,952,000 samples; the caption revision mix comparison has correlation0.99999997 /72.34dB SNR. Human listening is not attested. User approval is recorded for Reels01/02; Reel03 is ready for review. The delivery contains Instagram copy and per-export measured evidence.

## Reel-04 finishing — 20 October 2026

The user supplied Hands_near_serum_bottle_1080p_20261020002603.mp4 and Macro_slide_of_skincare_textures_20261020002912.mp4 and requested Reel-04. Both originals are preserved with SHA-256 provenance and LFS. A separate aspect-preserving B01 framing derivative excludes the baked festival title/corner symbol, avoiding overlap with the supplied transparent clinic mark; the original remains unchanged. Embedded sparkles remain. B01 runs1.300–6.500s (media1.200–6.400s); B02 runs14.500–20.600s (media0.200–6.300s), with original doctor narration and discarded B-roll audio.

The active clean plan is v03: closer framing on9785 and a wider9786 closing crop preserve the final forward lean. Two parallel parent/inheritance asides are omitted for pace; both skin-type “हो सकता है” qualifications and the complete suitability “ज़रूरी नहीं है” remain. Restore context before इसका, and retain the oily span continuously. The actual closing says to share Diwali happiness/sweets rather than skincare; no unrecorded Happy Bhai Dooj line is inserted from the script.

Finished review finish-v01 contains116 mixed-language words in31 semantic groups, approved white/gold and selective italic type, dark ink on ivory inserts, supplied transparent logo and the quiet original instrumental/ducking profile. Duration41.166667s /1235frames, full decode and A/V duration checks passed, no black intervals; measured−16.0LUFS /−1.5dBTP. All caption groups, source and insert boundaries, large framing/contrast proofs and consecutive animation samples reviewed. Original enhanced voice retains1,976,000samples and zero measured lag. Independent encoded ASR recovers the ordered story, complete qualifications and closing; human listening is not attested. Original media and earlier clean versions remain. Delivery includes current timeline, measured QA, edit notes and Instagram copy.

## Reel-04 user retake correction — 20 October2026

The user identified “इसका मतलब” around11s as a false first attempt. Current clean v04 /finish-v02 removes source12.600–14.300s, retaining replacement “इसका answer…” from14.300s at timeline10.100s. Exactly51frames /1.700s removed. All other wording, crops, caption styles, B-roll source ranges, logo and music settings are unchanged; B02 and downstream captions move earlier1.700s. Current duration39.466667s /1184frames,114words /30groups. Full decode and visual boundary/caption checks pass; no black intervals; −16.0LUFS /−1.5dBTP. Retained clean PCM is bit-identical outside6ms fade; minimum retained enhanced-voice window correlation0.999972. Full and isolated encoded decoding support the correction and retained qualifications; human listening is not attested. Earlier exports remain. This explicit user correction supersedes old ASR/editorial retention of the retake.

## Reels05–06 finishing — 20 October2026

Five attachments supplied four unique clips: skincare products, shoes/court, doorway basketball and sports-prop still life. The two basketball attachments are byte-identical, both paths preserved in provenance; one canonical asset is reused. All four originals are checksummed/LFS, continuously decoded and chronologically reviewed. Native sound is discarded; supplied sparkle and fictional labels remain. No family/child likeness or result is generated.

Reel05 current clean v02 /finish-v02:71.866667s /2156frames,189words /53caption groups. Restore onset context before Usually and tanning and correct the ASR-stretched बिल्कुल timing. The recorded product/sunscreen/serum statements remain for review rather than being replaced with a script; height/development wording is recovered by isolated decoding. B01 uses13.000–18.333s (media0.100–5.433s), a seven-frame dissolve, and ends before the later extra travel-product reveal. Court B02 uses31.200–37.700s (media0.200–6.700s) with a soft wipe.

Reel06 current clean v03 /finish-v02:37.733333s /1132frames,103words /27groups. Omit the optional unclear opening name/filler and repeated comparison; retain the complete comes-first/skincare contrast and final tanning/development qualification. Existing source-clock tracked framing follows the large sideways movement. Doorway B01 uses0.300–7.400s (media0.800–7.900s) and exits in the pause after the complete son quote; sports-prop B02 uses23.800–28.333s (media0.400–4.933s). The two cuts inside inserts are fully source-mapped.

Both use the approved Dhiraj white/gold and selective italic word system, dark ink on ivory, supplied transparent logo, original quiet instrumental with ducking and conservative6dB voice cleanup. Sports-insert type is slightly scaled to keep complete glyphs in the safe zone. All80 current encoded caption groups, every source/B-roll boundary, larger framing/contrast proofs and consecutive motion/word-entry samples inspected. Full clean/finished decodes pass, exact A/V durations, no black intervals; both final mixes measure−16.0LUFS /−1.5dBTP. Voice counts are3,449,600 and1,811,200samples, both zero measured enhancement lag. Full independent encoded v01 decoding recovers ordered speech/complete endings; current v02 uses identical enhanced voice masters. Mix correlations are0.99999999977 /0.999995518 respectively; Reel06 moves only a quiet exit cue. Human listening is not attested. Current handoffs include timelines, measured QA, edit notes and Instagram copy. All previous media and the Reel04 user retake correction remain preserved.

## Remaining batch finishing —20 October2026

The user supplied all12 remaining B-rolls and asked to finish Reels07–12 while retaining previous corrections. All are now finished reviews in Dhiraj-Edits. The approved Dhiraj premium captions, supplied transparent logo, conservative original-voice cleanup, quiet instrumental/ducking and source-aware podcast crops remain. Full source and returned-clip chronological inspection, independent long/short decoding, every encoded caption/cut/insert contact and selected consecutive motion samples support the edits. Human listening and clinical verification are not attested. See docs/DHIRAJ_QA_LESSONS.md for the retained workflow improvements.

- Reel07:clean-v04 /finish-v02,69.267s. Replace failed बालों को बीच की with the full Hair breakage pickup at50.233; omit production chatter and the false closing lead-in; refined closing source20.433 onward retains complete खुद से treatment…board certified dermatologist qualification.
- Reel08:clean-v03 /finish-v01,57.700s. End at the complete brand/trust point; omit the hesitant repeated autobiographical aside.
- Reel09:clean-v02 /finish-v01,47.400s. Restore word onsets, omit the optional unclear name apposition and preliminary budget quote; retain the complete1500/1200 procedure example and quality/reputation closing.
- Reel10:clean-v02 /finish-v01,66.700s. Podcast speaker cuts follow actual turns; remove Start and the first suitable बनेगा self-correction; preserve skin-type suitability and not-necessarily-expensive qualification.
- Reel11:clean-v02 /finish-v01,57.067s. Restore So onset and retain complete wedding/skincare closing before production command. Recorded2–4 and3–4 ranges belong to this recording.
- Reel12:clean-v04 /finish-v01,78.000s. Preserve full word onsets and parent–child turns. Restore साथ, parent करो, child खेलता हूँ and complete Okay; Hindi captions follow original speech rather than automatic translation.

Returned filenames are not reliable semantic labels: R011 is Reel10 gel footage; R0102 is Reel11 travel overhead; R012/R0122 reverse skincare/sports. Canonical asset provenance records each actual source path/hash and inspected subject. All supplied originals and previous delivery versions remain. Received native sparkle/fictional label-like marks are retained; B-roll sound is discarded.

All six final encodes measure−16.0LUFS /−1.5dBTP, decode completely at1080×1920/30fps, have exact planned frame/A-V duration counts and no black intervals. Enhanced voice master sample counts and zero measured lag are recorded per export. Local detailed evidence:02_analysis/dhiraj/reels-07-12-finishing. The toolkit's portable check passes68 script folders; catalog counts156 shared assets /42 motion kinds /50 clinic media; asset checksums/LFS exclusions are audited. No commit/push or publishing was performed.

Reel06 remains on the explicit user correction clean-v04 /finish-v03:36.500s, first joint fumble removed. Reel04's इसका मतलब retake removal and Reel01's5–10 correction remain selected.
