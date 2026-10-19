# Clinic reel workflow

- Current request (2026-10-19) authorises new tools/models and generated transparent illustrations behind the doctor, as well as relevant toolkit assets. User may supply video B-roll from the requested prompts. This supersedes the older user-generated-assets-only restriction for Reel-09 and the reusable reference pipeline. Do not invent clinic branding, treatment claims or patient results. Preserve supplied originals.
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

## Dhiraj batch approved style

- The user approved Dhiraj Reel-01 finish-v04 and asked to continue Reel-02 with that caption styling; font/layout tweaks are allowed. Use `styles/dhiraj-approved-v01.json` and `tools/dhiraj_premium_captions.py` for this batch. Clean white/gold type, selective editorial italic, measured word builds and dark ink on ivory inserts are the approved Dhiraj baseline, separately from the older My Dental baseline.
- Reel-01's opening range is **5–10**, explicitly corrected by the user; earlier ASR 15 and old exports do not override it. `Dhiraj-Sir-R01.mp4` was attached accidentally in place of Reel-02 B01 and is not a request to roll back caption style.
- Use the Dhiraj-supplied transparent clinic logo; never substitute the historical My Dental logo/outro. `03_reels/dhiraj/style-approval.json` records the applicable user clarification.

- For subsequent Dhiraj work, read `docs/DHIRAJ_QA_LESSONS.md`. Preserve explicit user number/retake corrections; check short source windows around repeated words and each cut, and match returned B-roll by actual subject rather than filename. Active/finishing plan maps govern current revisions.

## Historical clinic ending and voice finishing

- The reference ending supplied on17 October2026 is authorised in Reel-07 and Reel-08, including its spoken signature. Reuse only the extracted end-card asset; keep the complete reference reel local. Never overlap the signature with the doctor's last line.
- Apply conservative DeepFilterNet3 cleanup with exact sample-count and delay checks. Preserve original speech, pitch and speed; do not synthesize replacements. Add tail context before compensated inference to preserve the final phoneme. Stronger suppression is not automatically better; retain comparison evidence and listening limitations.
- The two received Reel-08 demonstrations (brushing/paste and flossing) are authorised for the edit and LFS backup. Do not substitute the earlier implant/bridge visuals for these hygiene explanations.

## Latest GitHub backup instruction — 20 October 2026

The owner confirmed the existing public remote, then explicitly excluded final edited videos: back up reusable supplied B-roll and toolkit/assets only. Reusable music/SFX remain included; personal dialogue recordings, final audio mixes, clean/final client videos, raw footage and caches stay local. Preserve all local originals.
