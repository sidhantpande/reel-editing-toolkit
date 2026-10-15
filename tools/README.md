# CLI tools

Primary AI workflow: [docs/AI_WORKFLOW.md](../docs/AI_WORKFLOW.md). Run from the repository root.

| Command | Purpose |
|---|---|
| `bash tools/bootstrap.sh` | Restore pinned dependencies and ignored media links |
| `python3 tools/reelctl.py init --brand niolearn --id niolearn-topic --source /absolute/main.mov` | Inventory/copy new source files and scaffold an edit |
| `python3 tools/reelctl.py assets --query clock` | Search original reusable assets |
| `python3 tools/reelctl.py scenes --query interview` | Find native editable scenes |
| `python3 tools/reelctl.py preflight PROJECT_FOLDER` | Check exact source cuts, word IDs/timings and source hashes |
| `python3 tools/reelctl.py render PROJECT_FOLDER` | Render reviewed inputs and measured output/alpha checks |
| `python3 tools/reelctl.py record PROJECT_FOLDER --video exports/ID-FINAL.mp4 --visual-reviewed --dialogue-reviewed` | Record a result after actual visual/dialogue review |
| `python3 tools/reelctl.py scene KIND --seconds 4 --transparent --output exports/clip.webm` | Export an original transparent scene |
| `python3 tools/catalog.py` | Rebuild text/JSON indexes; no dashboard |
| `npm test` | Test media preflight failure modes |
| `npm run check` | Portable code/assets/timeline checks without historical footage |
| `npm run check:media` | Also require all historical source recordings |
| `python3 tools/git_audit.py` | Check Git candidates exclude raw/final/cache/environment files |

Lower-level tools: `assemble_reel.py`, `build_reviewed_timeline.py`, `prepare_reel_finish.py`, `render.mjs`, `audio_finish.py`, `qa_reel.py`, `inspect_reel_finish.py`, `scan_reel_frames.py`, `inspect_motion.py`, `export_reviewed_assets.py`, `audit_alpha_assets.py`.

Transcription tools use Faster Whisper locally and download a requested model only when absent. ASR is a draft, not an approved caption. Historical batch tools rely on old media/outputs that are deliberately absent from the assets-only private backup. Use the generic reelctl workflow for new recordings.
