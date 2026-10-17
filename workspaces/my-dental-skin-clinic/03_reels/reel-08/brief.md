# Reel-08 — Mahagauri / daily dental hygiene

Latest status: 54.6-second A-roll edit prepared in the approved Reel-07 v05 style. Eight selected speech runs, 153 normalized draft caption words and seven short picture dissolves. Awaiting two newly generated brushing/flossing B-roll assets; prompts are ready in `05_broll_requests/prompts.md`. This is an A-roll review, not the completed B-roll edit.

## Source review and arrangement

| Source | Duration | Role / decision |
|---|---:|---|
| 0101 | 97.51 s | Main recording. Keep the complete “हर एक दाँत ज़रूरी होता है” hook, Mahagauri/purity connection and practical hygiene sections. Omit recap lead-in, long reading pauses, redundant comparison, repeated night-brushing explanation and the post-speech setup tail. |
| 0102 | 8.19 s | Selected closing: “तो जितने अच्छे से आप dental hygiene maintain करोगे, उतना ही आप cavities से बचोगे.” Keep 0–6.1 s; remove ending hold. |
| 0103 | 29.57 s | Alternate campaign-outro pickup with repeated attempts and silent screen-reading. It says “remember the day one … जहाँ से start किया था”; this “start” is part of the recorded sentence, not automatically a production command. Omit the whole alternate in favour of the direct hygiene closing. |

Sequence: tooth-value hook → Mahagauri/purity → twice-daily brushing / fluoride toothpaste → after-meal rinsing → hydration → all surfaces / interdental flossing → mouthwash → hygiene/cavities closing. Exact source ranges, crops, hashes, words and B-roll placements: `04_timeline/v01/plan.json` and `selects.csv`.

## Picture and captions

Use the approved top-left transparent logo, Mukta ExtraBold Hindi + Montserrat ExtraBold English, tight glyph-measured word spacing, variable emphasis and white/yellow progressive captions. No production/“3D illustration” labels. Picture joins use six-frame source-handle dissolves; narration is assembled as exact PCM slices with six-ms edge fades.

0101 crop: x216/y480/w1296/h2304. 0102 crop: x270/y900/w1188/h2112, independently calibrated to its lower subject framing. Source contact sheets, denser gaze sheets and crop comparison were inspected. B01's opening establishing shot is reserved for the hook's down-glance; the A-roll-only preview still shows that camera footage until the new clip is received. Other obvious long screen-reading intervals/tails are omitted.

## Transcript checks and limits

The small model was substantially unreliable on this quiet recording. An independently pinned large-v3-turbo model improved the clinical sections; hashes/revision are in `01_catalog/turbo-model.json`. Draft word text normalizes obvious misspellings (दाँत, महागौरी, fluoride, interdental, flossing, hygiene). Low-confidence connector/corrupted ASR tokens are noted in the plan rather than treated as verified speech. No human listening is available in this session; source-linked ASR/caption review remains explicit. The A-roll preview is for pacing/placement, and final caption/audio review is required after B-roll delivery.

## Two requested assets

- B01 brushing: 10 s vertical; 7 s main insert at 11.87–18.87 s, with a separate opening establishing section available at 0–2.3 s.
- B02 flossing: 10 s vertical; approximately 5.33 s insert at 33.23–38.57 s.

No implant/bridge footage is substituted for hygiene demonstrations. Both requested assets must be delivered and inspected before the full-render gate passes. User generates them; source originals remain unchanged.
