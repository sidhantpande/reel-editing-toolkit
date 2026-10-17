# Clinic pipeline

The full staged workflow is maintained at [`../../../docs/EDITING_PIPELINE.md`](../../../docs/EDITING_PIPELINE.md), from repository root. Approved clinic rules: [`APPROVED_STYLE.md`](APPROVED_STYLE.md).

1. Doctor and source registration.
2. Complete source review; independently check commands, retakes and gaze.
3. Arrange exact source-aware dialogue/word plan.
4. Send 1–2 anchored B-roll prompts to the user.
5. Inspect returned assets, hash and register them in the LFS-backed asset manifest.
6. Preflight; pending B-roll blocks a full render.
7. Render the approved logo, tight word captions and short dissolves.
8. Review encoded dialogue, gaze, captions, transitions and duration; version revisions.
9. Commit/push only reusable assets, provenance, code, plans, fonts and styles.

For difficult Hindi/Hinglish audio, restore the pinned higher-capacity model with `.venv/bin/python tools/fetch_model.py --model turbo`. Limit a repeat transcription to new footage, for example `tools/clinic.py transcribe --model turbo --source-folder /absolute/Reel-08 --redo`; its output remains a draft, not approved wording. Recording commands need independent snippet checks even with the larger model.
