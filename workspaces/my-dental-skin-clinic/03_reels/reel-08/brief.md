# Reel-08 — Mahagauri / daily dental hygiene

Latest status: v04 completed review assembly with both received brushing/flossing videos, the exact supplied white logo ending/spoken signature and conservative6 dB DeepFilterNet3 voice cleanup. Main narration54.6 s; finished export58.9667 s. Output: `05_exports/review/reel-08_review_v04-voice-outro.mp4`. Eight narration runs and151 normalized caption words in37 curated phrases retained. Technical/ASR/visual checks recorded; human listening remains unavailable.

## Source review and arrangement

| Source | Duration | Role / decision |
|---|---:|---|
| 0101 | 97.51 s | Main recording. Keep the complete “हर एक दाँत ज़रूरी होता है” hook, Mahagauri/purity connection and practical hygiene sections. Omit recap lead-in, long reading pauses, redundant comparison, repeated night-brushing explanation and the post-speech setup tail. |
| 0102 | 8.19 s | Selected closing: “तो जितने अच्छे से आप dental hygiene maintain करोगे, उतना ही आप cavities से बचोगे.” Keep 0–6.1 s; remove ending hold. |
| 0103 | 29.57 s | Alternate campaign-outro pickup with repeated attempts and silent screen-reading. It says “remember the day one … जहाँ से start किया था”; this “start” is part of the recorded sentence, not automatically a production command. Omit the whole alternate in favour of the direct hygiene closing. |

Sequence: tooth-value hook → Mahagauri/purity → twice-daily brushing / fluoride toothpaste → after-meal rinsing → hydration → all surfaces / interdental flossing → mouthwash → hygiene/cavities closing. Exact source ranges, crops, hashes, words and B-roll placements: `04_timeline/v04/plan.json` and `selects.csv`.

## Picture and captions

Use the approved top-left transparent logo, Mukta ExtraBold Hindi + Montserrat ExtraBold English, tight glyph-measured word spacing, variable emphasis and white/yellow progressive captions. No production/“3D illustration” labels. Picture joins use six-frame source-handle dissolves; narration is assembled as exact PCM slices with six-ms edge fades.

0101 crop: x216/y480/w1296/h2304. 0102 crop: x270/y900/w1188/h2112, independently calibrated to its lower subject framing. Source contact sheets, denser gaze sheets and crop comparison were inspected. B01's opening brushing shot is fully opaque from the first frame and covers the hook's down-glance in the completed v04 edit. Other obvious long screen-reading intervals/tails are omitted.

## Transcript checks and limits

The small model was substantially unreliable on this quiet recording. An independently pinned large-v3-turbo model improved the clinical sections; hashes/revision are in `01_catalog/turbo-model.json`. Draft word text normalizes obvious misspellings (दाँत, महागौरी, fluoride, interdental, flossing, hygiene). Low-confidence connector/corrupted ASR tokens are noted in the plan rather than treated as verified speech. No human listening is available in this session; source-linked ASR/caption review remains explicit. The delivered v04 export is ready for user review; source and export QA record these verification limits.

## Two requested assets

- B01 brushing: 10 s vertical; 7 s main insert at 11.87–18.87 s, with a separate opening establishing section available at 0–2.3 s.
- B02 flossing: 10 s vertical; approximately 5.33 s insert at 33.23–38.57 s.

Both supplied hygiene demonstrations have now been delivered and inspected; the full-render gate passes. No implant/bridge footage is substituted. Sources remain unchanged. See v04/plan.json for the source-aware, hard-cut-avoiding B-roll selection and v04/finishing for ending/audio QA.

## Delivered B-roll decisions

Brushing/paste delivery:16.76 s,720×1280/25 fps. Use5.4–7.7 s for the hook,0.4–4.2333 s for paste,4.8–8.2 s for brushing and8.6–12.5 s for inside surfaces. Baked scene cuts at4.32/8.52/12.68/14.76 s are avoided. Paste stays opaque under the incoming brushing dissolve; no A-roll flash-through.

Flossing delivery:24.312 s,720×1280/30 fps. Use1.2–6.5333 s on the interdental/flossing line. No internal scene cuts were detected in the received flossing clip. Both native audio tracks are discarded; narration continues. Approved copies and hashes are in the LFS-backed manifest.

## Caption curation after encoded review

In v04, phrases follow complete clauses and stop at sentence/take boundaries. The overlapping turbo chunks had introduced a stray बहुत from the excluded preceding sentence and a second clean token for the same50.92–51.34 s source phoneme. Independent retained-phrase ASR starts आपको दो बार; remove those two caption artefacts only. All54.6 s of narration remain unchanged. The preflight now rejects overlapping identical tokens; real repetitions at separate times remain valid. The earlier v03 export is retained locally as history.
