# My Dental & Skin Clinic editing workspace

Part of the private **reel-editing-toolkit** repository. The user-approved baseline is Reel-07 v05 (17 October 2026): top-left transparent logo, compact Mukta/Montserrat word captions, tight dialogue and short dissolves. Read [the approved style](docs/APPROVED_STYLE.md) and [the staged pipeline](../../docs/EDITING_PIPELINE.md).

## Current work

- Reel-07 v05 picture style approved; v06 adds the user-supplied ending and conservative voice cleanup. Local review exports are preserved in `05_exports/review/`.
- Reel-08 v04: both supplied hygiene B-rolls inserted; white logo ending/spoken signature and voice cleanup included. Main narration54.6 s; full review58.97 s. Analysis and exact source ranges live in `03_reels/reel-08/`.
- Approved Reel-07 implant/bridge and Reel-08 brushing/flossing B-roll MP4s, plus the extracted reusable logo ending, are backed up through Git LFS. B-roll checksums are in `04_generated_broll/manifest.json`.
- Camera files, reference videos, analysis media, exports, caches and model weights stay local. Git restores editing assets/decisions, not missing recordings.

## Commands

From repository root:

```sh
python3 tools/pipeline.py clinic doctor
python3 tools/pipeline.py clinic intake /absolute/path/to/new-footage
python3 tools/pipeline.py clinic analyse
python3 tools/pipeline.py clinic transcribe --language auto
python3 tools/pipeline.py clinic assets --query implant
python3 tools/pipeline.py clinic status
```

The workspace runtime can be restored with `bash workspaces/my-dental-skin-clinic/tools/bootstrap.sh`. Dependencies are pinned in `requirements.lock`; it installs locally and restores the pinned small model plus the configured turbo accuracy fallback (approximately 2 GB of local model data in total). Model revision/checksum metadata is in `01_catalog/turbo-model.json`. No model/venv files are tracked in Git.

After the source-aware plan is reviewed:

```sh
python3 tools/pipeline.py clinic preflight workspaces/my-dental-skin-clinic/03_reels/reel-08/04_timeline/v04/plan.json
python3 tools/pipeline.py clinic render workspaces/my-dental-skin-clinic/03_reels/reel-08/04_timeline/v04/plan.json
```

For new reels awaiting delivery, `--aroll-only` explicitly produces a preview. A full render fails if any requested media is missing. Finishing runs automatically for configured reels after the base render. A-roll previews never burn production labels/placeholders into the picture.

## Files and portability

- `01_catalog/`: source hashes, metadata, human notes and environment reports.
- `02_analysis/`: local decoded audio, contact sheets and draft ASR.
- `03_reels/<id>/`: story, cue/gaze decisions, source-aware timeline/words, B-roll prompts and QA.
- `styles/clinic-approved.json`, `docs/APPROVED_STYLE.md`: canonical clinic defaults.
- `00_inbox/brand/`: only the two supplied/derived clinic logo assets are allowed into Git.
- `assets/fonts/`: fonts, source metadata and OFL licences.
- `04_generated_broll/approved/`: approved reusable media tracked by LFS.
- `05_exports/`: versioned local review/final videos; never uploaded by Git.

Originals remain in place and unchanged. Source records use local paths; restore recordings and update paths on another computer. `/Users/sidhant/Desktop/Editing/my-dental-skin-reels` remains a local compatibility symlink after integration into this repository. The retained Reel-07 scripts preserve earlier revisions; new edits use `tools/render_clinic_reel.py` and an explicit plan. Direct listening limits are recorded in each reel's QA rather than disguised as verified captions.
