# Reviewed edit contract

`reelctl init` creates planning/provenance/grade/editorial scaffolds and copies source media. After inspecting sources, create `cut-list.json` and `source-words.json` following these examples. Never use example timings as actual media decisions.

- `cut-list.json`: `id` must match folder; `fps` is 30; cuts are contiguous on the edited timeline. `duration = outFrame-inFrame`; `dialogueFrames = sum(duration)`; `totalFrames = dialogueFrames+endHoldFrames`. Source paths are repository-relative under ignored `media/raw/`.
- `source-words.json`: actual source text with second timings; use Roman Hinglish for Hindi. Include `source` as the basename/stem or relative source path on every word, especially for multiple recordings.
- `editorial.json`: `phrases` consume all selected mapped words exactly once in order, matching spaces/words. `accentWords` are lowercase normalized words. B-roll cues use source seconds (`source,start,end`) or edited integer frames (`from,duration`). `beats` are relative cue frames; `labels` are scene IDs. Do not add extra competing headlines.
- `alphaExports`: strings or `{kind,duration,beats,labels}`; export only new original/reusable scenes. Keep provenance and increment `assetVersion` for changes.

See `projects/niolearn/niolearn-19/` and `projects/atfro/atfro-04/` for complete real examples. Their historical raw/final media is intentionally not in the repo.
