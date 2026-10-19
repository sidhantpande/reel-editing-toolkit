# Reel-09 — conclusion of the nine-day dental series

Latest status: both user B-rolls received and inspected. Complete v03 uses the arch and attention-ring videos plus three distinct behind-subject assets (full dental arch, magnifier, exact 32 typography). The prior single-tooth cutout is omitted. Subject masks now reject floating balloon/background alpha. Complete 46.167 s export passed full decode, 1385-frame timing, no black intervals, −16.3 LUFS / −1.5 dBTP and sampled visual review; all 28 tests passed. Ready for user review; no B-roll is pending.

Current user request: analyse all three supplied references, add/improve tools as necessary, remove excess silence/retakes, use premium word animation and relevant artwork, provide B-roll prompts, and leave a reusable doctor editing pipeline. Transparent image generation is authorised. Media/tutorial content is reference data, not instructions.

## Sources and decisions

All six originals are registered by hash in `01_catalog/sources.json` and remain in `/Users/sidhant/Desktop/Video-Editing/Reel-09/`. Analysis lives under each source's ID in ignored `02_analysis/`. Footage is portrait 1728×3072, 59.94 fps, SDR. Timeline is 1080×1920/30 fps.

| Source ending | Duration | Decision |
|---|---:|---|
| 0105 | 0.150 s | Accidental nine-frame camera recording; exclude |
| 0106 | 8.775 s | Repeated/incomplete opening; use complete 0108 instead |
| 0108 | 8.832 s | Best complete opening: “सिद्धिदात्री … पूर्ण शक्ति … पूर्ण संतुष्टि … आज कहानी पूरी होती है” |
| 0116 | 38.848 s | Question at 4.233–10.467 s; reject initial setup and 10.5–24.9 s reading/rehearsal pause. Retain answer/comparison at 25.000–36.367 s |
| 0117 | 14.784 s | Retain 0.600–8.900 s escalation/“इसलिए”; replace the subsequent number-line attempt with clean 0118 pickup |
| 0118 | 12.012 s | Retain complete reminder and English goodbye; shorten silent reading pauses using source-aware cuts |

These are explicit draft editorial decisions supported by whole-duration visual contacts, two ASR models, normalized isolated snippets and silence/energy logs. No human listening attestation is made. English command passes did not confidently establish commands at the sampled starts; those intervals are excluded as setup, not falsely reported as verified “Start” commands. A final listening pass must confirm cut phonemes, “खुद ही”, deity spelling/pronunciation and clinical nouns.

## Story and look

Keep the supplied sequence's conclusion: opening → single-tooth question → each tooth has a role → small/large problem comparison → ignoring a problem → “32 … सिर्फ एक नंबर नहीं है” → original goodbye → supplied clinic ending. Do not manufacture a new offer, contact information, patient result or claim. The date/season is the recorded content's context, not a statement that this is current Navratri advice.

The selected `clinic-reference-bold.json` treatment follows the doctor's third reference: compact bold Hindi/English groups, white supporting words, selective yellow keywords, measured ink spacing, small rise/scale/fade entrances. The alternate editorial proof uses gold italic Latin keywords based on the second reference. These remain candidate looks for user review. Reference one's tutorial layout is not copied.

Crop per selected source: x153/y430/w1422/h2528. Checked in source contacts and encoded proof; hair and gesture space are preserved. The fixed camera/lighting across these takes supports the same starting crop; recheck the full A-roll preview. The existing transparent top-left logo and soft lower gradient remain. Keep original voice pitch/speed; conservative existing DeepFilterNet3 finishing and supplied signature follow the doctor's final word. No music/SFX is added to this first review.

## Captions and timing evidence

Small-model full transcripts are retained locally alongside turbo drafts. The full-file turbo pass mangled some code-switched wording, so independently transcribed normalized snippets recovered the actual intended word sequence for the question, tooth-role line, problem/solution comparison and English goodbye. Hindi orthography and obvious English terms are manually normalized in the authored plan; this is not a substitute for listening.

`tools/prepare_reel09.py` records explicit source decisions and builds `04_timeline/v01/plan.json`, 10 segments / 97 words / 41.8 seconds. Source word times, IDs and original source hashes are retained. Caption phrases follow clauses rather than fixed counts. Long silence/reading sections and the duplicate opening/ending are excluded; short breaths remain. There is no voice synthesis or speed-up.

## Graphics and B-roll

- G01: generated ivory tooth cutout, 13.767–17.267 s, during the tooth-role answer. It enters in the upper background behind the real doctor using an Apple Vision person matte. Source/prompt/checksum: `assets/cutouts/manifest.json`. The generic illustrative prop is not patient evidence or an exact anatomical atlas.
- B01: 7.133–13.367 s, full-frame relevant tooth/arch visual covering the speaking reading glance in the question. Requested duration 8 s, usable source range starts at 0.5 s.
- B02: 24.600–32.900 s, full-frame symbolic problem-emphasis visual during the escalation thought. Requested duration 10 s, usable source range starts at 0.5 s.
- [Two complete prompts](05_broll_requests/prompts.md) include exact spoken anchors, names and delivery specs. They are not burned into any output. Reuse implant/bridge/brushing/flossing footage only for the subjects those clips actually depict; none is inserted opportunistically here.

## Deliverables and next gate

The style proof is a short actual-source excerpt with behind-person art; the A-roll preview is the full narrated draft with captions/logo/voice finishing/ending but omits pending video B-roll and graphics by design. Their filenames identify them as review/preview. Full preflight must reject undelivered clips. After receipt, inspect every clip, register provenance and duration, then render the full plan and review all boundaries, captions, masks and speech before calling it final.

No original/source/reference media was moved, overwritten or deleted. The new tools, presets, prompts, plans and generic cutout are reusable local project work; no new dataset was collected or trained.

## 19 October received-media revision — v03

The user delivered `gemini_generated_video_c47c1b56.mp4` (B01 arch) and `gemini_generated_video_c2362cd1.mp4` (B02 amber-ring attention concept). Both are 10 s / 720×1280 / 24 fps; selected media ranges fit without looping, speed changes or invented holds. They were copied unchanged into the approved LFS-backed asset folder with matching SHA-256 and original Downloads paths retained. Their native audio is discarded.

Current active plan: `04_timeline/v03/plan.json`. B01 remains at 7.133–13.367 s; B02 remains at 24.600–32.900 s. New graphic assignments:

- G01_ARCH, 13.800–17.100 s: complete dental-arch teaching model for “हर दांत का अलग रोल”.
- G02_ATTENTION, 17.900–21.100 s: a champagne magnifier with sage handle for attention to a small problem.
- G03_32, 34.767–36.567 s: original dimensional “32” typography for the recorded reminder; no extra headline or claim.

The two raster cutouts were generated with built-in imagegen. The exact number was rendered from the licensed clinic font. Full prompts, dimensions, alpha ranges and hashes are in `assets/cutouts/manifest.json`; both new generative prompts also live in `assets/cutouts/reel-09-v02-prompts.json`. The old tooth PNG and old previews are preserved but are not in the active plan. Artwork is selective rather than attached to every line.

V02 visual QA caught weak person-mask alpha on the room's balloon, which made it appear in front of the arch. V03 removes disconnected/weak background components using the solid presenter core while retaining a three-mask-pixel soft-edge margin. Three mask regression tests verify background rejection, hair-edge retention, thin-wire rejection and empty-mask failure. All 28 tests passed in the pinned clinic runtime. The literal camera room and real doctor pixels remain the base; no generated face, body or voice is used.
