# Clinic reel workflow

- User provides original footage and generates requested B-roll. Do not invent clinic assets or generate B-roll. User explicitly requested logo background removal on 2026-10-17; that asset edit is authorised. Preserve the supplied original separately.
- Watch/listen to supplied footage before grouping topics or choosing dialogue. Metadata, contact sheets and ASR are supporting evidence only.
- Give 1–2 B-roll prompts per reel, each linked to the exact spoken line, intended placement, duration and delivery filename. Wait for the returned clips before the final edit that uses them.
- Keep original files in place, unchanged. Register paths with `tools/clinic.py ingest`. Put all derived work in this workspace.
- Use `.venv/bin/python` and the full FFmpeg paths in `project.json`. Read the README and latest `01_catalog/setup-verification.json` for setup status.
- Reuse the prepared tools. Do not upgrade system packages or download large extra models without a concrete need.
- Draft transcripts require audio verification, especially Hindi/English mixing, clinical terms and names. Review before final captions.
- Do not add treatment claims, promises, patient outcomes, clinic contact details or before/after examples that the user has not supplied.
- Write per-reel source timestamps, decisions and B-roll requests in `03_reels/<id>/brief.md`. Keep the review CSV updated without discarding human notes.
- Export and review the full finished reel before marking it final. Default canvas is 1080×1920 at 30 fps; select source handling after inspection.

## Approved clinic default and multi-brand integration

- Read `docs/APPROVED_STYLE.md` and `styles/clinic-approved.json` before editing. Reel-07 v05 is the user-approved baseline; the earlier versions are not defaults. Top-left transparent logo; Mukta/Montserrat tight word captions; short dissolves. Never add the rejected “3D illustration” label.
- Every new take needs an independent recording-cue check. Never force an intended script over “Start” commands or decide edits using VAD alone. Record actual listening/ASR limitations.
- The workspace is part of the existing multi-brand Git repository under `workspaces/my-dental-skin-clinic`. Use `tools/pipeline.py` at repository root for the staged workflow. The old external workspace path remains a compatibility symlink.
- User-supplied approved B-roll MP4s are explicitly authorised for Git backup; track them with Git LFS and maintain checksums/provenance. Raw camera footage, reference reels, exports, analysis media, caches and environments remain excluded. No existing original or final media deletion is authorised by this request.
- Pending B-rolls must fail full-render preflight; an explicitly requested A-roll preview can omit them. Mark it as a preview and never paint placeholder labels in the video.
